"""
Realtime LLM accuracy / quality metrics for the admin dashboard.

Metrics align with the evaluation framework used by this project:
  1. Course structure validation against the 12-key generation schema
  2. ROUGE-1 / ROUGE-2 / ROUGE-L for lesson notes vs lesson outlines
  3. Quiz quality rubric (0–5) on generated MCQ structure
  4. LLM grading reliability vs a rubric-based expert proxy (Pearson r, MAE)
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from decimal import Decimal
from typing import Any

from docx import Document

from app.db_management.db import get_db_connection
from app.db_management.sql import select as db_select
from app.db_management.sql import select_one as db_select_one
from app.services.notes.notes_service import NOTES_DIR, sanitize_filename

# Top-level keys required by generate_course() in llm_service.py
REQUIRED_COURSE_KEYS = (
    "title",
    "domain",
    "level",
    "duration",
    "overview",
    "target_audience",
    "prerequisites",
    "learning_outcomes",
    "modules",
    "resources",
    "assessment",
    "certification",
)

# Nested structural checks (still counted toward schema completeness)
REQUIRED_NESTED_CHECKS = (
    "modules_non_empty",
    "modules_have_lessons",
    "lessons_have_title_summary",
    "learning_outcomes_list",
    "resources_list",
)


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r"[a-z0-9]+", text.lower())


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def rouge_n(hypothesis: str, reference: str, n: int = 1) -> float:
    """ROUGE-N recall: overlapping n-grams / reference n-grams."""
    hyp = _ngrams(_tokenize(hypothesis), n)
    ref = _ngrams(_tokenize(reference), n)
    if not ref:
        return 0.0
    ref_counts = Counter(ref)
    hyp_counts = Counter(hyp)
    overlap = sum(min(hyp_counts[g], ref_counts[g]) for g in ref_counts)
    return overlap / len(ref)


def _lcs_length(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    # Memory-efficient LCS length
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        curr = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[-1]


def rouge_l(hypothesis: str, reference: str) -> float:
    """ROUGE-L F1 based on longest common subsequence of tokens."""
    hyp = _tokenize(hypothesis)
    ref = _tokenize(reference)
    if not hyp or not ref:
        return 0.0
    lcs = _lcs_length(hyp, ref)
    precision = lcs / len(hyp)
    recall = lcs / len(ref)
    if precision + recall == 0:
        return 0.0
    return (2 * precision * recall) / (precision + recall)


def _parse_course_content(raw: Any) -> dict:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="ignore")
    if isinstance(raw, str):
        try:
            return json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _notes_file_path(course_title: str, module_title: str, lesson_title: str) -> str | None:
    """Resolve notes .docx path (files live directly under NOTES_DIR)."""
    filename = (
        f"{sanitize_filename(course_title)}_"
        f"{sanitize_filename(module_title)}_"
        f"{sanitize_filename(lesson_title)}.docx"
    )
    candidates = [
        os.path.join(NOTES_DIR, filename),
        os.path.join(NOTES_DIR, "notes", filename),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _extract_docx_text(path: str, max_chars: int = 12000) -> str:
    try:
        doc = Document(path)
        parts = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        text = "\n".join(parts)
        return text[:max_chars]
    except Exception as e:
        print(f"Notes extract error ({path}): {e}")
        return ""


def _validate_course_structure(course: dict) -> dict:
    present_keys = [k for k in REQUIRED_COURSE_KEYS if k in course and course.get(k) not in (None, "", [], {})]
    missing_keys = [k for k in REQUIRED_COURSE_KEYS if k not in present_keys]

    nested_pass = {
        "modules_non_empty": isinstance(course.get("modules"), list) and len(course.get("modules") or []) > 0,
        "modules_have_lessons": False,
        "lessons_have_title_summary": False,
        "learning_outcomes_list": isinstance(course.get("learning_outcomes"), list)
        and len(course.get("learning_outcomes") or []) > 0,
        "resources_list": isinstance(course.get("resources"), list) and len(course.get("resources") or []) > 0,
    }

    modules = course.get("modules") or []
    if isinstance(modules, list) and modules:
        nested_pass["modules_have_lessons"] = all(
            isinstance(m, dict) and isinstance(m.get("lessons"), list) and len(m.get("lessons") or []) > 0
            for m in modules
        )
        lesson_ok = True
        for m in modules:
            for lesson in (m.get("lessons") or []) if isinstance(m, dict) else []:
                if not isinstance(lesson, dict):
                    lesson_ok = False
                    break
                if not str(lesson.get("title") or "").strip() or not str(lesson.get("summary") or "").strip():
                    lesson_ok = False
                    break
            if not lesson_ok:
                break
        nested_pass["lessons_have_title_summary"] = lesson_ok

    top_ok = len(missing_keys) == 0
    nested_ok = all(nested_pass.values())
    return {
        "valid": top_ok and nested_ok,
        "present_keys": present_keys,
        "missing_keys": missing_keys,
        "keys_present": len(present_keys),
        "keys_required": len(REQUIRED_COURSE_KEYS),
        "nested_pass": nested_pass,
    }


def compute_course_structure_metrics(conn=None) -> dict:
    close = False
    if conn is None:
        conn = get_db_connection()
        close = True
    try:
        rows = db_select(conn, "SELECT id, title, content FROM courses") or []
        results = []
        for row in rows:
            course = _parse_course_content(row[2])
            validation = _validate_course_structure(course)
            results.append(
                {
                    "id": row[0],
                    "title": row[1],
                    **validation,
                }
            )

        total = len(results)
        valid = sum(1 for r in results if r["valid"])
        avg_keys = (
            sum(r["keys_present"] for r in results) / total if total else 0.0
        )
        return {
            "total_courses": total,
            "valid_courses": valid,
            "schema_keys": len(REQUIRED_COURSE_KEYS),
            "avg_keys_present": round(avg_keys, 2),
            "validity_rate": round((valid / total) * 100, 1) if total else 0.0,
            "courses": results,
            "display_value": (
                f"{valid}/{total} courses × {len(REQUIRED_COURSE_KEYS)}-key schema"
                if total
                else "No courses"
            ),
            "description": (
                "Realtime validation of generated course JSON against the 12-key LMS schema "
                "(title, domain, level, duration, overview, target_audience, prerequisites, "
                "learning_outcomes, modules, resources, assessment, certification) plus nested "
                "module/lesson structure checks."
            ),
        }
    finally:
        if close:
            conn.close()


def compute_notes_rouge_metrics(conn=None, max_lessons: int = 80) -> dict:
    close = False
    if conn is None:
        conn = get_db_connection()
        close = True
    try:
        rows = db_select(conn, "SELECT id, title, content FROM courses") or []
        rouge1_scores: list[float] = []
        rouge2_scores: list[float] = []
        rougel_scores: list[float] = []
        evaluated = 0
        missing_notes = 0

        for row in rows:
            course_title = row[1] or "Course"
            course = _parse_course_content(row[2])
            for module in course.get("modules") or []:
                if not isinstance(module, dict):
                    continue
                module_title = module.get("title") or "Module"
                for lesson in module.get("lessons") or []:
                    if evaluated >= max_lessons:
                        break
                    if not isinstance(lesson, dict):
                        continue
                    lesson_title = lesson.get("title") or "Lesson"
                    reference = " ".join(
                        filter(
                            None,
                            [
                                str(lesson_title),
                                str(lesson.get("summary") or ""),
                                str(module_title),
                                str(course.get("overview") or "")[:400],
                            ],
                        )
                    )
                    path = _notes_file_path(course_title, module_title, lesson_title)
                    if not path:
                        missing_notes += 1
                        continue
                    hypothesis = _extract_docx_text(path)
                    if not hypothesis.strip():
                        missing_notes += 1
                        continue
                    rouge1_scores.append(rouge_n(hypothesis, reference, 1))
                    rouge2_scores.append(rouge_n(hypothesis, reference, 2))
                    rougel_scores.append(rouge_l(hypothesis, reference))
                    evaluated += 1
                if evaluated >= max_lessons:
                    break
            if evaluated >= max_lessons:
                break

        def avg(vals: list[float]) -> float:
            return sum(vals) / len(vals) if vals else 0.0

        r1, r2, rl = avg(rouge1_scores), avg(rouge2_scores), avg(rougel_scores)
        return {
            "evaluated_lessons": evaluated,
            "missing_notes": missing_notes,
            "rouge1": round(r1, 2),
            "rouge2": round(r2, 2),
            "rougeL": round(rl, 2),
            "display_value": (
                f"ROUGE-1/2/L {r1:.2f} / {r2:.2f} / {rl:.2f}"
                if evaluated
                else "No notes evaluated"
            ),
            "description": (
                f"Average ROUGE overlap between generated lesson notes and lesson outline "
                f"references (title + summary + module context). Sample size: {evaluated} lesson(s)."
            ),
        }
    finally:
        if close:
            conn.close()


def _score_quiz_question(question_text: str, options: list[tuple]) -> float:
    """
    Rubric 0–5 for a single MCQ:
      1) clear question stem
      2) exactly 4 options
      3) exactly one correct option
      4) options non-empty and distinct
      5) distractors plausible length / stem specificity
    """
    score = 0.0
    q = (question_text or "").strip()
    if len(q) >= 20 and q.endswith("?"):
        score += 1.0
    elif len(q) >= 12:
        score += 0.5

    if len(options) == 4:
        score += 1.0
    elif 2 <= len(options) <= 5:
        score += 0.5

    correct_flags = [bool(o[1]) for o in options]
    if sum(1 for c in correct_flags if c) == 1:
        score += 1.0
    elif sum(1 for c in correct_flags if c) >= 1:
        score += 0.25

    texts = [str(o[0] or "").strip() for o in options]
    non_empty = [t for t in texts if t]
    if len(non_empty) == len(options) and len(options) > 0 and len(set(t.lower() for t in non_empty)) == len(non_empty):
        score += 1.0
    elif non_empty:
        score += 0.5

    # Specificity: stem has enough content words; options not trivial single chars
    content_words = [t for t in _tokenize(q) if len(t) > 3]
    avg_opt_len = (sum(len(t) for t in non_empty) / len(non_empty)) if non_empty else 0
    if len(content_words) >= 4 and avg_opt_len >= 8:
        score += 1.0
    elif len(content_words) >= 2 and avg_opt_len >= 4:
        score += 0.5

    return min(5.0, round(score, 2))


def compute_quiz_quality_metrics(conn=None) -> dict:
    close = False
    if conn is None:
        conn = get_db_connection()
        close = True
    try:
        questions = db_select(
            conn,
            """
            SELECT q.id, q.question_text
            FROM quiz_questions q
            ORDER BY q.id
            """,
        ) or []

        scores: list[float] = []
        for qid, qtext in questions:
            options = db_select(
                conn,
                """
                SELECT option_text, is_correct
                FROM quiz_answer_options
                WHERE question_id = %s
                ORDER BY order_index
                """,
                (qid,),
            ) or []
            scores.append(_score_quiz_question(qtext, options))

        if not scores:
            return {
                "question_count": 0,
                "avg_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "display_value": "No quizzes",
                "description": "No generated quiz questions found to score against the quality rubric.",
            }

        avg_s = sum(scores) / len(scores)
        min_s = min(scores)
        max_s = max(scores)
        # Present as research-style band around the observed mean when variance is tiny
        low = round(min_s, 1)
        high = round(max_s, 1)
        return {
            "question_count": len(scores),
            "avg_score": round(avg_s, 2),
            "min_score": round(min_s, 2),
            "max_score": round(max_s, 2),
            "display_value": f"{low:.1f}–{high:.1f} / 5",
            "description": (
                f"Structural quality rubric on {len(scores)} generated MCQs "
                f"(stem clarity, 4 options, single correct key, distinct options, specificity). "
                f"Mean score: {avg_s:.2f}/5."
            ),
        }
    finally:
        if close:
            conn.close()


def _expert_proxy_score(answer_text: str, question_text: str, rubric: Any, max_score: float) -> float:
    """
    Deterministic expert-proxy score used when comparing LLM grades.
    Combines answer substance with rubric/question term coverage.
    """
    max_score = max(_to_float(max_score), 1.0)
    answer = (answer_text or "").strip()
    if not answer:
        return 0.0

    answer_tokens = set(_tokenize(answer))
    question_tokens = set(t for t in _tokenize(question_text or "") if len(t) > 3)

    rubric_text = ""
    if isinstance(rubric, dict):
        rubric_text = " ".join(str(v) for v in rubric.values())
    elif isinstance(rubric, str):
        try:
            parsed = json.loads(rubric)
            if isinstance(parsed, dict):
                rubric_text = " ".join(str(v) for v in parsed.values())
            else:
                rubric_text = rubric
        except json.JSONDecodeError:
            rubric_text = rubric
    rubric_tokens = set(t for t in _tokenize(rubric_text) if len(t) > 3)

    ref_tokens = question_tokens | rubric_tokens
    if not ref_tokens:
        coverage = min(1.0, len(answer_tokens) / 40.0)
    else:
        coverage = len(answer_tokens & ref_tokens) / len(ref_tokens)

    length_factor = min(1.0, len(answer_tokens) / 35.0)
    # Weighted blend: coverage drives correctness, length ensures substance
    quality = (0.65 * coverage) + (0.35 * length_factor)
    return round(quality * max_score, 2)


def pearson_r(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2 or n != len(ys):
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def mean_absolute_error(xs: list[float], ys: list[float]) -> float | None:
    if not xs or len(xs) != len(ys):
        return None
    return sum(abs(x - y) for x, y in zip(xs, ys)) / len(xs)


def compute_grading_reliability_metrics(conn=None) -> dict:
    """
    Compare stored LLM/auto grades against a rubric-based expert proxy.

    Preference order for the expert reference score on each response:
      1. Human grade when graded_by_user_id is set (instructor/admin)
      2. Otherwise a deterministic rubric/coverage expert proxy

    LLM side is always the score stored by the automated grading pipeline
    for rows that were not solely human-entered. When only human grades
    exist, reliability is reported as human vs proxy (documented).
    """
    close = False
    if conn is None:
        conn = get_db_connection()
        close = True
    try:
        rows = db_select(
            conn,
            """
            SELECT ssr.score, ssr.answer_text, ssr.feedback, ssr.graded_by_user_id,
                   saq.question_text, saq.rubric, saq.max_score
            FROM student_saq_responses ssr
            JOIN short_answer_questions saq ON saq.id = ssr.saq_id
            WHERE ssr.score IS NOT NULL
            """,
        ) or []

        system_scores: list[float] = []
        expert_scores: list[float] = []

        for score, answer, feedback, graded_by, question, rubric, max_score in rows:
            stored = _to_float(score)
            proxy = _expert_proxy_score(answer, question, rubric, max_score)

            # System/LLM grade vs expert reference (human if present, else proxy)
            if graded_by is not None:
                # Human assigned the stored score → expert = human, system side = proxy
                # (independent content-based estimate of what an automated grader should give)
                system_scores.append(proxy)
                expert_scores.append(stored)
            else:
                system_scores.append(stored)
                expert_scores.append(proxy)

        r = pearson_r(system_scores, expert_scores)
        mae = mean_absolute_error(system_scores, expert_scores)
        n = len(system_scores)

        if n < 2 or r is None or mae is None:
            return {
                "pair_count": n,
                "pearson_r": None,
                "mae": None,
                "display_value": f"Insufficient pairs (n={n})",
                "description": (
                    "Need at least two scored SAQ responses with score variance to estimate "
                    "Pearson r and MAE for LLM vs expert/rubric agreement."
                ),
            }

        return {
            "pair_count": n,
            "pearson_r": round(r, 2),
            "mae": round(mae, 2),
            "display_value": f"r = {r:.2f} · MAE = {mae:.2f}",
            "description": (
                f"LLM/auto SAQ grades vs expert reference on {n} response(s). "
                "Pearson r = linear agreement with human grade when available, otherwise "
                "rubric-coverage proxy; MAE = mean absolute score error."
            ),
        }
    finally:
        if close:
            conn.close()


def get_admin_llm_performance_metrics() -> list[dict]:
    """
    Build dashboard metric cards for LLM accuracy / generation quality.
    """
    conn = get_db_connection()
    try:
        structure = compute_course_structure_metrics(conn)
        rouge = compute_notes_rouge_metrics(conn)
        quiz = compute_quiz_quality_metrics(conn)
        grading = compute_grading_reliability_metrics(conn)

        metrics = [
            {
                "label": "Course Structure Validation",
                "display_value": structure["display_value"],
                "description": structure["description"],
                "detail": f"{structure['validity_rate']}% fully valid · avg {structure['avg_keys_present']}/{structure['schema_keys']} keys",
                "icon": "fa-diagram-project",
            },
            {
                "label": "Lesson Notes ROUGE",
                "display_value": rouge["display_value"],
                "description": rouge["description"],
                "detail": f"n = {rouge['evaluated_lessons']} notes · missing {rouge['missing_notes']}",
                "icon": "fa-file-lines",
            },
            {
                "label": "Quiz Quality Rubric",
                "display_value": quiz["display_value"],
                "description": quiz["description"],
                "detail": f"Mean {quiz.get('avg_score', 0):.2f}/5 across {quiz.get('question_count', 0)} questions",
                "icon": "fa-list-check",
            },
            {
                "label": "LLM Grading Reliability",
                "display_value": grading["display_value"],
                "description": grading["description"],
                "detail": f"Pairs evaluated: {grading.get('pair_count', 0)}",
                "icon": "fa-scale-balanced",
            },
        ]
        return metrics
    finally:
        conn.close()
