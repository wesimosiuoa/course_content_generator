"""
Evaluation framework metrics for the admin dashboard.

Matrix (Automatic vs Manual):
  - Generation Time      Automatic ✅  | Manual ❌
  - Completeness         Automatic ✅  | Manual optional (expert /5)
  - Relevance            Automatic ✅  | Manual optional (expert /5)
  - Hallucination Rate   Automatic optional (heuristics) | Manual optional
  - Usability (SUS)      Automatic from survey scores | Manual survey input
  - Learning Gain        Automatic (pre/post quiz delta) | Manual optional
"""

from __future__ import annotations

import json
import re
import time
from decimal import Decimal
from typing import Any, Optional
from urllib.parse import urlparse

import os

from docx import Document

from app.db_management.db import get_db_connection
from app.db_management.sql import insert as db_insert
from app.db_management.sql import select as db_select
from app.db_management.sql import select_one as db_select_one
from app.services.notes.notes_service import NOTES_DIR, sanitize_filename

# Expected structural density for completeness
EXPECTED_MODULES = 5
EXPECTED_LESSONS_PER_MODULE = 3
EXPECTED_OUTCOMES = 5
EXPECTED_RESOURCES = 5

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

HALLUCINATION_MARKERS = (
    "lorem ipsum",
    "todo",
    "tbd",
    "placeholder",
    "example.com",
    "your text here",
    "insert content",
    "n/a",
    "xxx",
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


def _parse_json(raw: Any) -> dict:
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


def ensure_evaluation_tables(conn=None) -> None:
    """Create evaluation tables if they do not exist."""
    close = False
    if conn is None:
        conn = get_db_connection()
        close = True
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_logs (
              id INT(11) NOT NULL AUTO_INCREMENT,
              user_id INT(11) DEFAULT NULL,
              generation_type VARCHAR(32) NOT NULL,
              duration_ms INT(11) NOT NULL,
              success TINYINT(1) NOT NULL DEFAULT 1,
              meta_json TEXT DEFAULT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (id),
              KEY idx_generation_type (generation_type),
              KEY idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sus_responses (
              id INT(11) NOT NULL AUTO_INCREMENT,
              user_id INT(11) NOT NULL,
              q1 TINYINT NOT NULL,
              q2 TINYINT NOT NULL,
              q3 TINYINT NOT NULL,
              q4 TINYINT NOT NULL,
              q5 TINYINT NOT NULL,
              q6 TINYINT NOT NULL,
              q7 TINYINT NOT NULL,
              q8 TINYINT NOT NULL,
              q9 TINYINT NOT NULL,
              q10 TINYINT NOT NULL,
              sus_score DECIMAL(5,2) NOT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (id),
              KEY idx_sus_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS manual_evaluations (
              id INT(11) NOT NULL AUTO_INCREMENT,
              course_id INT(11) DEFAULT NULL,
              evaluator_id INT(11) DEFAULT NULL,
              metric_name VARCHAR(64) NOT NULL,
              score DECIMAL(6,2) NOT NULL,
              max_score DECIMAL(6,2) NOT NULL DEFAULT 5.00,
              notes TEXT DEFAULT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (id),
              KEY idx_manual_metric (metric_name),
              KEY idx_manual_course (course_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
    finally:
        cursor.close()
        if close:
            conn.close()


def log_generation(
    generation_type: str,
    duration_ms: int,
    success: bool = True,
    user_id: Optional[int] = None,
    meta: Optional[dict] = None,
) -> None:
    """Persist a generation timing event (automatic Generation Time metric)."""
    try:
        conn = get_db_connection()
        ensure_evaluation_tables(conn)
        db_insert(
            conn,
            """
            INSERT INTO generation_logs (user_id, generation_type, duration_ms, success, meta_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_id,
                generation_type,
                int(max(0, duration_ms)),
                1 if success else 0,
                json.dumps(meta or {}),
            ),
        )
        conn.close()
    except Exception as e:
        print(f"log_generation error: {e}")


class GenerationTimer:
    """Context helper: with GenerationTimer('course', user_id) as t: ..."""

    def __init__(self, generation_type: str, user_id: Optional[int] = None, meta: Optional[dict] = None):
        self.generation_type = generation_type
        self.user_id = user_id
        self.meta = meta or {}
        self.success = True
        self._start = 0.0
        self.duration_ms = 0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.duration_ms = int((time.perf_counter() - self._start) * 1000)
        self.success = exc_type is None and self.success
        log_generation(
            self.generation_type,
            self.duration_ms,
            success=self.success,
            user_id=self.user_id,
            meta=self.meta,
        )
        return False


def compute_sus_score(answers: list[int]) -> float:
    """
    Standard SUS scoring (Brooke, 1996).
    answers: 10 items on 1–5 Likert scale.
    Odd items (1,3,5,7,9): score = response - 1
    Even items (2,4,6,8,10): score = 5 - response
    Total * 2.5 → 0–100
    """
    if len(answers) != 10:
        raise ValueError("SUS requires exactly 10 answers")
    contrib = 0
    for i, raw in enumerate(answers):
        v = max(1, min(5, int(raw)))
        if i % 2 == 0:
            contrib += v - 1
        else:
            contrib += 5 - v
    return round(contrib * 2.5, 2)


def save_sus_response(user_id: int, answers: list[int]) -> float:
    ensure_evaluation_tables()
    score = compute_sus_score(answers)
    conn = get_db_connection()
    try:
        db_insert(
            conn,
            """
            INSERT INTO sus_responses
            (user_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, sus_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, *answers, score),
        )
        return score
    finally:
        conn.close()


# Expert (manual) metrics that humans should rate — not generation time.
EXPERT_METRICS = (
    {
        "key": "completeness",
        "label": "Completeness",
        "icon": "fa-layer-group",
        "max_score": 5,
        "higher_is_better": True,
        "who": "Domain expert / instructor / admin",
        "what_to_review": "Generated course structure, modules, lessons, outcomes, and resources.",
        "rubric": [
            "1 — Critical sections missing; unusable outline",
            "2 — Major gaps (few modules/lessons or empty outcomes)",
            "3 — Usable but incomplete (thin lessons or sparse resources)",
            "4 — Mostly complete; minor omissions only",
            "5 — Full LMS-ready structure with rich outcomes and resources",
        ],
        "how": "Open the course preview/content. Check title, domain, modules, lesson summaries, learning outcomes, resources, assessment, certification.",
    },
    {
        "key": "relevance",
        "label": "Relevance",
        "icon": "fa-bullseye",
        "max_score": 5,
        "higher_is_better": True,
        "who": "Domain expert familiar with the topic and learner goals",
        "what_to_review": "Alignment of content with stated domain, topic, level, and learner goals.",
        "rubric": [
            "1 — Off-topic or wrong domain",
            "2 — Loosely related; weak match to goals",
            "3 — Generally on-topic; some drift",
            "4 — Strong match to topic/level with minor drift",
            "5 — Tightly aligned to preferences and learning goals",
        ],
        "how": "Compare course overview and modules to the generation preferences (domain, topic, goal, level).",
    },
    {
        "key": "hallucination",
        "label": "Hallucination / factual risk",
        "icon": "fa-shield-halved",
        "max_score": 5,
        "higher_is_better": False,
        "who": "Subject-matter expert (fact-checking)",
        "what_to_review": "False claims, fake citations/URLs, invented tools, or placeholder content.",
        "rubric": [
            "1 — Almost no factual issues (best)",
            "2 — Minor questionable claims",
            "3 — Several unsupported statements or weak sources",
            "4 — Frequent errors or fabricated resources",
            "5 — Severe hallucination; content not trustworthy (worst)",
        ],
        "how": "Spot-check lesson claims and resource links. Flag invented authors, dead/fake URLs, or domain-false statements. Lower score is better.",
    },
    {
        "key": "learning_gain",
        "label": "Learning gain (expert judgment)",
        "icon": "fa-arrow-trend-up",
        "max_score": 5,
        "higher_is_better": True,
        "who": "Instructor / education expert",
        "what_to_review": "Whether progression, quizzes, and materials would support measurable learning.",
        "rubric": [
            "1 — Unlikely to produce learning gain",
            "2 — Weak progression; poor assessment alignment",
            "3 — Some scaffolding; moderate potential",
            "4 — Clear progression and assessment path",
            "5 — Strong pedagogical design for measurable gain",
        ],
        "how": "Review module order, lesson depth, and assessments. Optionally compare early vs later quiz results for that course.",
    },
    {
        "key": "usability",
        "label": "Usability (expert UX judgment)",
        "icon": "fa-hand-pointer",
        "max_score": 5,
        "higher_is_better": True,
        "who": "UX reviewer / instructor walking the learner path",
        "what_to_review": "Ease of navigating and consuming generated materials (not the full SUS survey).",
        "rubric": [
            "1 — Confusing / hard to use",
            "2 — Frequent friction",
            "3 — Acceptable with some friction",
            "4 — Smooth for most tasks",
            "5 — Excellent clarity and flow",
        ],
        "how": "Walk the learner path: open course → lessons → notes/quiz. Rate clarity of labels, structure, and flow. End-users should still complete the SUS survey separately.",
    },
)

EXPERT_METRIC_KEYS = {m["key"] for m in EXPERT_METRICS}

# Nielsen's 10 usability heuristics (used in admin course review UI + expert checklist)
NIELSEN_HEURISTICS = (
    {
        "id": 1,
        "name": "Visibility of system status",
        "prompt": "Does the course clearly show progress, structure, and where the learner is (modules, lessons, completion)?",
    },
    {
        "id": 2,
        "name": "Match between system and the real world",
        "prompt": "Is language familiar to learners? Do examples and domain terms match the real world of the topic?",
    },
    {
        "id": 3,
        "name": "User control and freedom",
        "prompt": "Can learners navigate freely (back, skip sections, leave a lesson) without getting trapped?",
    },
    {
        "id": 4,
        "name": "Consistency and standards",
        "prompt": "Are module/lesson layouts, labels, and assessment patterns consistent throughout the course?",
    },
    {
        "id": 5,
        "name": "Error prevention",
        "prompt": "Do quizzes/SAQs prevent confusion (clear stems, one correct answer, sensible distractors)?",
    },
    {
        "id": 6,
        "name": "Recognition rather than recall",
        "prompt": "Are objectives, key concepts, and resources visible when needed so learners need not memorize navigation?",
    },
    {
        "id": 7,
        "name": "Flexibility and efficiency of use",
        "prompt": "Can advanced learners scan summaries/resources quickly while beginners still get guided structure?",
    },
    {
        "id": 8,
        "name": "Aesthetic and minimalist design",
        "prompt": "Is content focused and uncluttered—essential material first, without noisy filler?",
    },
    {
        "id": 9,
        "name": "Help users recognize, diagnose, and recover from errors",
        "prompt": "Would wrong quiz answers or weak SAQ feedback help a learner recover and understand mistakes?",
    },
    {
        "id": 10,
        "name": "Help and documentation",
        "prompt": "Are overviews, outcomes, prerequisites, and resources enough to support independent learning?",
    },
)


def get_expert_metric_definitions() -> list[dict]:
    return list(EXPERT_METRICS)


def get_nielsen_heuristics() -> list[dict]:
    return list(NIELSEN_HEURISTICS)


def _resolve_notes_path(course_title: str, module_title: str, lesson_title: str) -> Optional[str]:
    filename = (
        f"{sanitize_filename(course_title)}_"
        f"{sanitize_filename(module_title)}_"
        f"{sanitize_filename(lesson_title)}.docx"
    )
    for path in (
        os.path.join(NOTES_DIR, filename),
        os.path.join(NOTES_DIR, "notes", filename),
    ):
        if os.path.isfile(path):
            return path
    return None


def _docx_preview(path: str, max_chars: int = 800) -> str:
    try:
        doc = Document(path)
        parts = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        text = "\n".join(parts)
        if len(text) > max_chars:
            return text[:max_chars].rstrip() + "…"
        return text
    except Exception:
        return ""


def get_admin_course_review(course_id: int) -> Optional[dict]:
    """
    Full course package for admin/expert review inside the admin panel:
    structure, lessons, notes availability, quizzes, SAQs, resources.
    """
    conn = get_db_connection()
    try:
        row = db_select_one(
            conn,
            "SELECT id, title, description, content, created_at FROM courses WHERE id = %s",
            (course_id,),
        )
        if not row:
            return None

        content = _parse_json(row[3])
        course_title = row[1] or content.get("title") or f"Course {course_id}"
        modules_out = []
        total_lessons = 0
        notes_ready = 0
        quiz_total = 0

        for mi, module in enumerate(content.get("modules") or []):
            if not isinstance(module, dict):
                continue
            module_title = module.get("title") or f"Module {mi + 1}"
            lessons_out = []
            for li, lesson in enumerate(module.get("lessons") or []):
                if not isinstance(lesson, dict):
                    continue
                total_lessons += 1
                lesson_title = lesson.get("title") or f"Lesson {li + 1}"
                notes_path = _resolve_notes_path(course_title, module_title, lesson_title)
                has_notes = bool(notes_path)
                if has_notes:
                    notes_ready += 1

                q_count_row = db_select_one(
                    conn,
                    """
                    SELECT COUNT(*) FROM quiz_questions
                    WHERE course_id = %s AND module_index = %s AND lesson_index = %s
                    """,
                    (course_id, mi, li),
                )
                q_count = int(q_count_row[0]) if q_count_row else 0
                quiz_total += q_count

                sample_qs = db_select(
                    conn,
                    """
                    SELECT question_text FROM quiz_questions
                    WHERE course_id = %s AND module_index = %s AND lesson_index = %s
                    ORDER BY id LIMIT 3
                    """,
                    (course_id, mi, li),
                ) or []

                lessons_out.append(
                    {
                        "index": li,
                        "title": lesson_title,
                        "summary": lesson.get("summary") or "",
                        "has_notes": has_notes,
                        "notes_preview": _docx_preview(notes_path) if notes_path else "",
                        "quiz_count": q_count,
                        "sample_questions": [q[0] for q in sample_qs],
                    }
                )

            saq_rows = db_select(
                conn,
                """
                SELECT question_text, max_score FROM short_answer_questions
                WHERE course_id = %s AND module_index = %s
                ORDER BY id
                """,
                (course_id, mi),
            ) or []

            modules_out.append(
                {
                    "index": mi,
                    "title": module_title,
                    "description": module.get("description") or "",
                    "lessons": lessons_out,
                    "saqs": [
                        {"question": r[0], "max_score": _to_float(r[1])}
                        for r in saq_rows
                    ],
                }
            )

        resources = []
        for res in content.get("resources") or []:
            if isinstance(res, dict):
                resources.append(
                    {
                        "title": res.get("title") or "Resource",
                        "author": res.get("author") or "",
                        "url": res.get("url") or "",
                    }
                )

        return {
            "id": row[0],
            "title": course_title,
            "description": row[2] or "",
            "domain": content.get("domain") or "—",
            "level": content.get("level") or "—",
            "duration": content.get("duration") or "—",
            "overview": content.get("overview") or "",
            "target_audience": content.get("target_audience") or "",
            "prerequisites": content.get("prerequisites") or "",
            "learning_outcomes": content.get("learning_outcomes")
            if isinstance(content.get("learning_outcomes"), list)
            else [],
            "assessment": content.get("assessment") or "",
            "certification": content.get("certification") or "",
            "modules": modules_out,
            "resources": resources,
            "created_at": row[4].isoformat(sep=" ", timespec="minutes") if row[4] else "",
            "stats": {
                "module_count": len(modules_out),
                "lesson_count": total_lessons,
                "notes_ready": notes_ready,
                "quiz_questions": quiz_total,
                "resources": len(resources),
                "outcomes": len(content.get("learning_outcomes") or [])
                if isinstance(content.get("learning_outcomes"), list)
                else 0,
            },
            "heuristics": get_nielsen_heuristics(),
        }
    finally:
        conn.close()



def _existing_rating_row(conn, evaluator_id: Optional[int], course_id: Optional[int], metric_name: str):
    if evaluator_id is None:
        return None
    if course_id is None:
        return db_select_one(
            conn,
            """
            SELECT id FROM manual_evaluations
            WHERE evaluator_id = %s AND course_id IS NULL AND metric_name = %s
            LIMIT 1
            """,
            (evaluator_id, metric_name),
        )
    return db_select_one(
        conn,
        """
        SELECT id FROM manual_evaluations
        WHERE evaluator_id = %s AND course_id = %s AND metric_name = %s
        LIMIT 1
        """,
        (evaluator_id, course_id, metric_name),
    )


def get_evaluator_ratings_for_course(evaluator_id: int, course_id: Optional[int]) -> dict:
    """
    Map metric_name -> rating dict for this expert on this course (once).
    course_id=None means system-wide ratings.
    """
    ensure_evaluation_tables()
    conn = get_db_connection()
    try:
        if course_id is None:
            rows = db_select(
                conn,
                """
                SELECT metric_name, score, max_score, notes, created_at
                FROM manual_evaluations
                WHERE evaluator_id = %s AND course_id IS NULL
                """,
                (evaluator_id,),
            ) or []
        else:
            rows = db_select(
                conn,
                """
                SELECT metric_name, score, max_score, notes, created_at
                FROM manual_evaluations
                WHERE evaluator_id = %s AND course_id = %s
                """,
                (evaluator_id, course_id),
            ) or []
        out = {}
        for metric_name, score, max_score, notes, created_at in rows:
            out[metric_name] = {
                "score": _to_float(score),
                "max_score": _to_float(max_score) or 5.0,
                "notes": notes or "",
                "created_at": created_at.isoformat(sep=" ", timespec="minutes") if created_at else "",
            }
        return out
    finally:
        conn.close()


def evaluator_has_rated_course(evaluator_id: int, course_id: Optional[int]) -> bool:
    """True if this expert already submitted at least one metric for the course."""
    return bool(get_evaluator_ratings_for_course(evaluator_id, course_id))


def save_manual_evaluation(
    metric_name: str,
    score: float,
    evaluator_id: Optional[int] = None,
    course_id: Optional[int] = None,
    max_score: float = 5.0,
    notes: str = "",
    allow_update: bool = False,
) -> str:
    """
    Save one expert rating.
    Returns: 'inserted' | 'updated' | 'exists' | 'skipped'
    Experts rate a course once per metric (no duplicates unless allow_update).
    """
    ensure_evaluation_tables()
    conn = get_db_connection()
    try:
        existing = _existing_rating_row(conn, evaluator_id, course_id, metric_name)
        if existing and not allow_update:
            return "exists"
        if existing and allow_update:
            from app.db_management.sql import update as db_update

            db_update(
                conn,
                """
                UPDATE manual_evaluations
                SET score = %s, max_score = %s, notes = %s, created_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (score, max_score, notes or None, existing[0]),
            )
            return "updated"

        db_insert(
            conn,
            """
            INSERT INTO manual_evaluations
            (course_id, evaluator_id, metric_name, score, max_score, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (course_id, evaluator_id, metric_name, score, max_score, notes or None),
        )
        return "inserted"
    finally:
        conn.close()


def save_expert_rating_batch(
    ratings: list[dict],
    evaluator_id: Optional[int],
    course_id: Optional[int] = None,
) -> dict:
    """
    Save multiple expert metric ratings in one submit (once per course per expert).
    Returns {saved, skipped_existing, errors}.
    """
    saved = 0
    skipped = 0
    for item in ratings:
        key = (item.get("metric_name") or "").strip().lower()
        if key not in EXPERT_METRIC_KEYS:
            continue
        try:
            score = float(item.get("score"))
        except (TypeError, ValueError):
            continue
        max_score = float(item.get("max_score") or 5)
        score = max(0.0, min(max_score, score))
        notes = (item.get("notes") or "").strip()
        result = save_manual_evaluation(
            metric_name=key,
            score=score,
            evaluator_id=evaluator_id,
            course_id=course_id,
            max_score=max_score,
            notes=notes,
            allow_update=False,
        )
        if result == "inserted":
            saved += 1
        elif result == "exists":
            skipped += 1
    return {"saved": saved, "skipped_existing": skipped}


def list_courses_for_expert_rating(conn=None) -> list[dict]:
    close = False
    if conn is None:
        conn = get_db_connection()
        close = True
    try:
        rows = db_select(conn, "SELECT id, title, content FROM courses ORDER BY title")
        courses = []
        for row in rows or []:
            content = _parse_json(row[2]) if len(row) > 2 else {}
            courses.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "domain": content.get("domain") or "—",
                    "level": content.get("level") or "—",
                }
            )
        return courses
    finally:
        if close:
            conn.close()


def list_expert_ratings(limit: int = 50, course_id: Optional[int] = None) -> list[dict]:
    """Recent expert ratings with course/evaluator labels."""
    ensure_evaluation_tables()
    conn = get_db_connection()
    try:
        if course_id:
            rows = db_select(
                conn,
                """
                SELECT m.id, m.course_id, m.evaluator_id, m.metric_name, m.score, m.max_score,
                       m.notes, m.created_at, c.title, u.full_name
                FROM manual_evaluations m
                LEFT JOIN courses c ON c.id = m.course_id
                LEFT JOIN users u ON u.id = m.evaluator_id
                WHERE m.course_id = %s
                ORDER BY m.created_at DESC
                LIMIT %s
                """,
                (course_id, limit),
            ) or []
        else:
            rows = db_select(
                conn,
                """
                SELECT m.id, m.course_id, m.evaluator_id, m.metric_name, m.score, m.max_score,
                       m.notes, m.created_at, c.title, u.full_name
                FROM manual_evaluations m
                LEFT JOIN courses c ON c.id = m.course_id
                LEFT JOIN users u ON u.id = m.evaluator_id
                ORDER BY m.created_at DESC
                LIMIT %s
                """,
                (limit,),
            ) or []

        label_map = {m["key"]: m["label"] for m in EXPERT_METRICS}
        results = []
        for row in rows:
            results.append(
                {
                    "id": row[0],
                    "course_id": row[1],
                    "evaluator_id": row[2],
                    "metric_name": row[3],
                    "metric_label": label_map.get(row[3], row[3]),
                    "score": _to_float(row[4]),
                    "max_score": _to_float(row[5]) or 5.0,
                    "notes": row[6] or "",
                    "created_at": row[7].isoformat(sep=" ", timespec="minutes") if row[7] else "",
                    "course_title": row[8] or "System-wide (no course)",
                    "evaluator_name": row[9] or "Unknown",
                }
            )
        return results
    finally:
        conn.close()


def expert_rating_coverage_summary() -> dict:
    """How many expert ratings exist per metric / course."""
    ensure_evaluation_tables()
    conn = get_db_connection()
    try:
        by_metric = db_select(
            conn,
            """
            SELECT metric_name, COUNT(*), AVG(score), AVG(max_score)
            FROM manual_evaluations
            GROUP BY metric_name
            """,
        ) or []
        courses_rated = db_select_one(
            conn,
            "SELECT COUNT(DISTINCT course_id) FROM manual_evaluations WHERE course_id IS NOT NULL",
        )
        total = db_select_one(conn, "SELECT COUNT(*) FROM manual_evaluations")
        total_courses = db_select_one(conn, "SELECT COUNT(*) FROM courses")
        metric_stats = {}
        for name, cnt, avg_s, avg_max in by_metric:
            metric_stats[name] = {
                "count": int(cnt),
                "avg_score": round(_to_float(avg_s), 2),
                "max_score": round(_to_float(avg_max) or 5, 2),
            }
        return {
            "total_ratings": int(total[0]) if total else 0,
            "courses_rated": int(courses_rated[0]) if courses_rated and courses_rated[0] else 0,
            "total_courses": int(total_courses[0]) if total_courses else 0,
            "by_metric": metric_stats,
        }
    finally:
        conn.close()


def _manual_avg(conn, metric_name: str) -> Optional[dict]:
    try:
        row = db_select_one(
            conn,
            """
            SELECT AVG(score), AVG(max_score), COUNT(*)
            FROM manual_evaluations
            WHERE metric_name = %s
            """,
            (metric_name,),
        )
    except Exception:
        return None
    if not row or not row[2]:
        return None
    return {
        "avg_score": round(_to_float(row[0]), 2),
        "max_score": round(_to_float(row[1]) or 5.0, 2),
        "count": int(row[2]),
    }


def _format_manual(manual: Optional[dict], unit: str = "/5") -> str:
    if not manual:
        return "❌ No expert ratings yet"
    return f"{manual['avg_score']:.1f}{unit} (n={manual['count']})"


# ---------------------------------------------------------------------------
# Automatic metric computers
# ---------------------------------------------------------------------------

def compute_generation_time(conn) -> dict:
    try:
        rows = db_select(
            conn,
            """
            SELECT generation_type, AVG(duration_ms), COUNT(*),
                   MIN(duration_ms), MAX(duration_ms)
            FROM generation_logs
            WHERE success = 1
            GROUP BY generation_type
            """,
        ) or []
        overall = db_select_one(
            conn,
            """
            SELECT AVG(duration_ms), COUNT(*)
            FROM generation_logs
            WHERE success = 1
            """,
        )
    except Exception:
        rows, overall = [], None

    by_type = {}
    for gen_type, avg_ms, cnt, min_ms, max_ms in rows:
        by_type[gen_type] = {
            "avg_ms": round(_to_float(avg_ms), 0),
            "count": int(cnt),
            "min_ms": int(min_ms or 0),
            "max_ms": int(max_ms or 0),
        }

    n = int(overall[1]) if overall and overall[1] else 0
    avg_ms = _to_float(overall[0]) if overall and overall[0] is not None else None

    if n == 0 or avg_ms is None:
        auto = "No timed runs yet"
        detail = "Generate a course to start collecting automatic timing data."
    else:
        seconds = avg_ms / 1000.0
        auto = f"{seconds:.1f}s avg (n={n})"
        parts = [f"{k}: {v['avg_ms']/1000:.1f}s" for k, v in by_type.items()]
        detail = " · ".join(parts) if parts else f"n={n} successful generations"

    return {
        "metric": "Generation Time",
        "automatic": auto,
        "automatic_enabled": True,
        "manual": "❌ N/A",
        "manual_enabled": False,
        "detail": detail,
        "description": "Wall-clock duration of LLM generation calls (course, notes, quiz, etc.). Manual authoring time is out of scope.",
        "icon": "fa-stopwatch",
        "by_type": by_type,
    }


def _course_completeness_score(course: dict) -> float:
    """Return completeness in 0–100 for one course."""
    checks = []

    # 12-key presence
    for key in REQUIRED_COURSE_KEYS:
        val = course.get(key)
        checks.append(1.0 if val not in (None, "", [], {}) else 0.0)

    modules = course.get("modules") if isinstance(course.get("modules"), list) else []
    # Module density (target 5)
    checks.append(min(1.0, len(modules) / EXPECTED_MODULES) if EXPECTED_MODULES else 0.0)

    # Lessons density
    if modules:
        lesson_ratios = []
        for m in modules:
            lessons = m.get("lessons") if isinstance(m, dict) else []
            if not isinstance(lessons, list):
                lessons = []
            lesson_ratios.append(min(1.0, len(lessons) / EXPECTED_LESSONS_PER_MODULE))
            for les in lessons:
                if isinstance(les, dict):
                    lesson_ratios.append(1.0 if str(les.get("title") or "").strip() else 0.0)
                    lesson_ratios.append(1.0 if str(les.get("summary") or "").strip() else 0.0)
        checks.append(sum(lesson_ratios) / len(lesson_ratios) if lesson_ratios else 0.0)
    else:
        checks.append(0.0)

    outcomes = course.get("learning_outcomes") if isinstance(course.get("learning_outcomes"), list) else []
    checks.append(min(1.0, len(outcomes) / EXPECTED_OUTCOMES))

    resources = course.get("resources") if isinstance(course.get("resources"), list) else []
    checks.append(min(1.0, len(resources) / EXPECTED_RESOURCES))

    return round(100.0 * (sum(checks) / len(checks)), 1) if checks else 0.0


def compute_completeness(conn) -> dict:
    rows = db_select(conn, "SELECT id, title, content FROM courses") or []
    scores = []
    for _id, _title, content in rows:
        scores.append(_course_completeness_score(_parse_json(content)))

    manual = _manual_avg(conn, "completeness")

    if not scores:
        auto = "No courses"
    else:
        avg = sum(scores) / len(scores)
        auto = f"{avg:.1f}% complete (n={len(scores)})"

    return {
        "metric": "Completeness",
        "automatic": auto,
        "automatic_enabled": True,
        "manual": _format_manual(manual),
        "manual_enabled": True,
        "detail": "Schema keys, module/lesson density, outcomes, and resources.",
        "description": "Automatic: structural completeness of generated course JSON against the expected LMS blueprint. Manual: expert completeness rating (/5).",
        "icon": "fa-layer-group",
        "scores": scores,
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def compute_relevance(conn) -> dict:
    """
    Relevance of generated content to learner intent:
    course text vs preferences (generated_from_preferences + user_preferences domains/topics).
    """
    rows = db_select(
        conn,
        """
        SELECT id, title, content, generated_from_preferences
        FROM courses
        """,
    ) or []

    scores: list[float] = []
    for _id, title, content, prefs_raw in rows:
        course = _parse_json(content)
        prefs = _parse_json(prefs_raw)

        course_text = " ".join(
            [
                str(title or ""),
                str(course.get("domain") or ""),
                str(course.get("title") or ""),
                str(course.get("overview") or ""),
                str(course.get("target_audience") or ""),
                " ".join(str(x) for x in (course.get("learning_outcomes") or []) if isinstance(course.get("learning_outcomes"), list)),
            ]
        )
        course_tokens = set(t for t in _tokenize(course_text) if len(t) > 2)

        pref_parts = []
        if prefs:
            for k in ("domain", "topic", "goal", "level", "prior_knowledge", "learning_preference"):
                v = prefs.get(k)
                if isinstance(v, list):
                    pref_parts.extend(str(x) for x in v)
                elif v:
                    pref_parts.append(str(v))
        pref_tokens = set(t for t in _tokenize(" ".join(pref_parts)) if len(t) > 2)

        if not pref_tokens:
            # Fallback: domain token self-consistency (title/overview vs domain field)
            domain_tokens = set(t for t in _tokenize(str(course.get("domain") or "")) if len(t) > 2)
            pref_tokens = domain_tokens

        if not course_tokens or not pref_tokens:
            continue

        # Blend Jaccard with coverage of preference terms in course
        jacc = _jaccard(course_tokens, pref_tokens)
        coverage = len(course_tokens & pref_tokens) / len(pref_tokens) if pref_tokens else 0.0
        scores.append(100.0 * (0.45 * jacc + 0.55 * coverage))

    manual = _manual_avg(conn, "relevance")
    if not scores:
        auto = "No preference-linked courses"
    else:
        avg = sum(scores) / len(scores)
        auto = f"{avg:.1f}% relevant (n={len(scores)})"

    return {
        "metric": "Relevance",
        "automatic": auto,
        "automatic_enabled": True,
        "manual": _format_manual(manual),
        "manual_enabled": True,
        "detail": "Token overlap of course content with learner preferences / domain intent.",
        "description": "Automatic: semantic/term alignment between generated course content and stated preferences. Manual: expert relevance rating (/5).",
        "icon": "fa-bullseye",
        "scores": scores,
    }


def _is_weak_url(url: str) -> bool:
    if not url or not str(url).strip():
        return True
    u = str(url).strip().lower()
    if any(m in u for m in ("example.com", "placeholder", "yoursite", "localhost")):
        return True
    try:
        parsed = urlparse(u if "://" in u else f"https://{u}")
        if not parsed.netloc or "." not in parsed.netloc:
            return True
    except Exception:
        return True
    return False


def compute_hallucination_rate(conn) -> dict:
    """
    Optional automatic fact-check heuristics (no live LLM call):
      - placeholder / lorem text in overviews and lesson summaries
      - weak or fake resource URLs
      - empty required narrative fields that claim substance
    Rate = flagged items / inspected items.
    """
    rows = db_select(conn, "SELECT id, title, content FROM courses") or []
    inspected = 0
    flagged = 0
    flag_details = []

    for cid, title, content in rows:
        course = _parse_json(content)
        texts = [
            ("overview", str(course.get("overview") or "")),
            ("assessment", str(course.get("assessment") or "")),
            ("certification", str(course.get("certification") or "")),
        ]
        for modules in (course.get("modules") or []):
            if not isinstance(modules, dict):
                continue
            for lesson in modules.get("lessons") or []:
                if isinstance(lesson, dict):
                    texts.append((f"lesson:{lesson.get('title')}", str(lesson.get("summary") or "")))

        for label, text in texts:
            inspected += 1
            low = text.lower().strip()
            if not low or len(_tokenize(low)) < 5:
                flagged += 1
                flag_details.append(f"thin:{label}")
                continue
            if any(m in low for m in HALLUCINATION_MARKERS):
                flagged += 1
                flag_details.append(f"marker:{label}")

        for res in course.get("resources") or []:
            if not isinstance(res, dict):
                continue
            inspected += 1
            url = str(res.get("url") or "")
            rtitle = str(res.get("title") or "")
            if _is_weak_url(url) or any(m in rtitle.lower() for m in HALLUCINATION_MARKERS):
                flagged += 1
                flag_details.append(f"resource:{rtitle[:40]}")

    manual = _manual_avg(conn, "hallucination")
    if inspected == 0:
        auto = "No content to inspect"
        rate = None
    else:
        rate = 100.0 * flagged / inspected
        auto = f"{rate:.1f}% flagged (optional)"

    manual_display = "❌ Optional — no ratings"
    if manual:
        # Lower hallucination score is better if experts rate "hallucination severity"
        manual_display = f"{manual['avg_score']:.1f}/{manual['max_score']:.0f} severity (n={manual['count']})"

    return {
        "metric": "Hallucination Rate",
        "automatic": auto,
        "automatic_enabled": True,  # optional heuristics always on
        "manual": manual_display,
        "manual_enabled": True,
        "optional": True,
        "detail": f"Inspected {inspected} content units · flagged {flagged} · heuristic fact-check (placeholders, thin text, weak URLs).",
        "description": "Optional automatic LLM-output risk heuristics (placeholder text, empty substance, dubious resource links). Manual expert fact-check scores optional.",
        "icon": "fa-shield-halved",
        "rate": rate,
        "flagged": flagged,
        "inspected": inspected,
    }


def compute_usability_sus(conn) -> dict:
    try:
        row = db_select_one(
            conn,
            "SELECT AVG(sus_score), COUNT(*), MIN(sus_score), MAX(sus_score) FROM sus_responses",
        )
    except Exception:
        row = None

    n = int(row[1]) if row and row[1] else 0
    if n == 0:
        auto = "No SUS responses"
        detail = "Collect System Usability Scale surveys from users (10 Likert items → 0–100)."
    else:
        avg = _to_float(row[0])
        auto = f"SUS {avg:.1f} / 100 (n={n})"
        detail = f"Range { _to_float(row[2]):.0f}–{_to_float(row[3]):.0f} · industry pass ~68"

    # Manual side is the survey instrument itself (human-completed)
    manual = f"✅ Survey instrument ({n} response{'s' if n != 1 else ''})" if n else "❌ No surveys submitted"

    return {
        "metric": "Usability (SUS)",
        "automatic": auto,
        "automatic_enabled": True,
        "manual": manual,
        "manual_enabled": True,
        "detail": detail,
        "description": "System Usability Scale (Brooke 1996). Users complete 10 items manually; the dashboard computes the 0–100 SUS score automatically.",
        "icon": "fa-hand-pointer",
        "response_count": n,
    }


def compute_learning_gain(conn) -> dict:
    """
    Learning gain from quiz performance:
    For each user-course, compare early lesson scores vs later lesson scores.
    gain = mean(later) - mean(early)
    Also reports overall pass rate as secondary signal.
    """
    rows = db_select(
        conn,
        """
        SELECT user_id, course_id, module_index, lesson_index,
               score_percentage, completed_at
        FROM lesson_quiz_results
        ORDER BY user_id, course_id, completed_at, module_index, lesson_index
        """,
    ) or []

    from collections import defaultdict

    grouped: dict[tuple, list[float]] = defaultdict(list)
    for user_id, course_id, _mi, _li, score, _ts in rows:
        grouped[(user_id, course_id)].append(_to_float(score))

    gains = []
    for key, scores in grouped.items():
        if len(scores) < 2:
            continue
        mid = max(1, len(scores) // 2)
        early = sum(scores[:mid]) / mid
        later = sum(scores[mid:]) / (len(scores) - mid)
        gains.append(later - early)

    manual = _manual_avg(conn, "learning_gain")

    if not gains:
        # Fallback: single-shot average if any quiz results
        if rows:
            avg_score = sum(_to_float(r[4]) for r in rows) / len(rows)
            auto = f"Avg quiz {avg_score:.1f}% (need ≥2 attempts/user for gain)"
        else:
            auto = "No quiz results"
    else:
        avg_gain = sum(gains) / len(gains)
        sign = "+" if avg_gain >= 0 else ""
        auto = f"{sign}{avg_gain:.1f} pp (n={len(gains)} paths)"

    return {
        "metric": "Learning Gain",
        "automatic": auto,
        "automatic_enabled": True,
        "manual": _format_manual(manual),
        "manual_enabled": True,
        "detail": "Pre/post style: later lesson quiz average minus earlier lesson quiz average per learner-course path.",
        "description": "Automatic learning gain from lesson quiz trajectories. Manual: expert or instructor-rated learning gain (/5).",
        "icon": "fa-arrow-trend-up",
        "gains": gains,
    }


def get_evaluation_matrix() -> list[dict]:
    """Return the full Automatic vs Manual evaluation matrix for the admin UI."""
    conn = get_db_connection()
    try:
        ensure_evaluation_tables(conn)
        return [
            compute_generation_time(conn),
            compute_completeness(conn),
            compute_relevance(conn),
            compute_hallucination_rate(conn),
            compute_usability_sus(conn),
            compute_learning_gain(conn),
        ]
    finally:
        conn.close()
