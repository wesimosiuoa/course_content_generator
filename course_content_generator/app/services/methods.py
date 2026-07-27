from flask import request, session, redirect, url_for, flash
from app.db_management.sql import select_one, insert, update, select_all
from app.db_management.db import get_db_connection
from app.services.profile_service import build_user_profile
from app.services.llm_service import generate_speech, generate_summary, generate_explanation
import hashlib
import json

def get_current_user_profile():
    if "user_id" not in session:
        return None
    return build_user_profile(session["user_id"])


def course_content_hash(course_data):
    """Stable hash for generated course JSON (dedupe on save)."""
    return hashlib.sha256(
        json.dumps(course_data, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def persist_generated_course(course_data, user_id=None, preferences=None):
    """
    Save generated course to the public catalog and return its id.
    Enrollment is separate — generating/saving does not enroll the creator.
    Other students can discover and enroll later (Discover / search).
    Does NOT put the full course JSON in the Flask session (cookie overflow
    would drop login state).
    """
    if not course_data or not isinstance(course_data, dict):
        raise ValueError("Invalid course data")

    content_hash = course_content_hash(course_data)
    description = (
        (course_data.get("description") or "").strip()
        or (course_data.get("overview") or "").strip()
        or ""
    )
    prefs_payload = preferences if preferences is not None else course_data.get("preferences") or {}

    conn = get_db_connection()
    try:
        existing = select_one(conn, """
            SELECT id FROM courses WHERE content_hash = %s
        """, (content_hash,))

        if existing:
            course_id = int(existing[0])
        else:
            insert(conn, """
                INSERT INTO courses (
                    title,
                    description,
                    content,
                    content_hash,
                    generated_from_preferences,
                    created_by,
                    is_public,
                    popularity_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, 1, 0)
            """, (
                course_data.get("title", "Generated Course"),
                description,
                json.dumps(course_data, default=str),
                content_hash,
                json.dumps(prefs_payload, default=str),
                user_id,
            ))
            row = select_one(conn, """
                SELECT id FROM courses WHERE content_hash = %s
            """, (content_hash,))
            if not row:
                raise Exception("Course insert failed — could not retrieve ID.")
            course_id = int(row[0])

        # Assign assistant instructor by expertise (for reevaluation / consultancy)
        try:
            assign_course_instructor(course_id)
        except Exception as assign_err:
            print("WARN assign instructor after persist:", assign_err)

        return course_id
    finally:
        conn.close()


def enroll_user_in_course(user_id, course_id):
    """Enroll once (INSERT IGNORE). Returns True if enrolled / already enrolled."""
    if not user_id or not course_id:
        return False
    conn = get_db_connection()
    try:
        insert(conn, """
            INSERT IGNORE INTO enrollments (user_id, course_id)
            VALUES (%s, %s)
        """, (user_id, course_id))
        return True
    except Exception as e:
        print("ERROR enrolling user:", e)
        return False
    finally:
        conn.close()


def load_course_content_by_id(course_id):
    """Load parsed course content JSON + metadata by id."""
    conn = get_db_connection()
    try:
        row = select_one(conn, """
            SELECT id, title, description, content, popularity_score
            FROM courses
            WHERE id = %s
        """, (course_id,))
        if not row:
            return None
        raw = row[3]
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", errors="ignore")
        if isinstance(raw, str):
            try:
                content = json.loads(raw)
            except Exception:
                content = {}
        elif isinstance(raw, dict):
            content = raw
        else:
            content = {}
        # Prefer full stored content for preview (title/overview live inside JSON)
        if isinstance(content, dict) and content:
            course = dict(content)
        else:
            course = {}
        course.setdefault("title", row[1])
        if row[2]:
            course.setdefault("description", row[2])
            course.setdefault("overview", row[2])
        course["id"] = int(row[0])
        course["popularity_score"] = row[4]
        return course
    except Exception as e:
        print("ERROR loading course content:", e)
        return None
    finally:
        conn.close()


def save_course_reaction():

    conn = get_db_connection()

    try:
        # 1️⃣ Ensure user logged in
        if "user_id" not in session:
            return "Unauthorized", 401

        user_id = session["user_id"]
        reaction = request.form.get("action")

        if reaction not in ["like", "dislike"]:
            return "Invalid reaction.", 400

        # Prefer small session course_id (avoids huge session payloads)
        course_id = request.form.get("course_id") or session.get("preview_course_id") or session.get("generated_course_id")
        if course_id:
            try:
                course_id = int(course_id)
            except (TypeError, ValueError):
                course_id = None

        if not course_id:
            course_data = session.get("generated_course")
            if not course_data:
                return "No course data found.", 400
            course_id = persist_generated_course(
                course_data,
                user_id=user_id,
                preferences=session.get("preferences"),
            )

        # Keep only lightweight keys in session (never full course JSON)
        session["preview_course_id"] = course_id
        session["generated_course_id"] = course_id
        session.pop("generated_course", None)
        if session.get("user_id"):
            session.permanent = True
            session.modified = True

        # SAFETY CHECK
        if not course_id:
            raise Exception("course_id is NULL after insert/select.")

        # 4️⃣ Check if user already reacted
        existing = select_one(conn, """
            SELECT id, reaction
            FROM course_feedback
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

        if existing:
            old_reaction = existing[1]

            if old_reaction != reaction:
                # Update reaction
                update(conn, """
                    UPDATE course_feedback
                    SET reaction = %s
                    WHERE id = %s
                """, (reaction, existing[0]))

                # Adjust popularity score correctly
                if reaction == "like":
                    update(conn, """
                        UPDATE courses
                        SET popularity_score = popularity_score + 2
                        WHERE id = %s
                    """, (course_id,))
                else:
                    update(conn, """
                        UPDATE courses
                        SET popularity_score = popularity_score - 2
                        WHERE id = %s
                    """, (course_id,))
        else:
            # Insert new reaction
            insert(conn, """
                INSERT INTO course_feedback (user_id, course_id, reaction)
                VALUES (%s, %s, %s)
            """, (user_id, course_id, reaction))

            # Adjust popularity score
            if reaction == "like":
                update(conn, """
                    UPDATE courses
                    SET popularity_score = popularity_score + 1
                    WHERE id = %s
                """, (course_id,))
            else:
                update(conn, """
                    UPDATE courses
                    SET popularity_score = popularity_score - 1
                    WHERE id = %s
                """, (course_id,))

        conn.commit()

        flash("Reaction saved successfully!", "success")
        
        # Redirect back to preview page to keep the flow smooth
        # Don't redirect to view_course which might break the session
        return redirect(url_for("main.preview_generated_course"))

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return "Something went wrong.", 500

    finally:
        conn.close()

def get_user_reaction(user_id, course_id):
    conn = get_db_connection()
    try:
        reaction = select_one(conn, """
            SELECT reaction
            FROM course_feedback
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

        return reaction[0] if reaction else None

    except Exception as e:
        print("ERROR fetching user reaction:", e)
        return None

    finally:
        conn.close()
def is_enrolled(user_id, course_id):
    conn = get_db_connection()
    try:
        enrollment = select_one(conn, """
            SELECT id
            FROM enrollments
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

        return bool(enrollment)

    except Exception as e:
        print("ERROR checking enrollment:", e)
        return False

    finally:
        conn.close()



# discover
def get_enrolled_course_ids(user_id):
    """Set of course IDs the student is already enrolled in (enrollment is once)."""
    if not user_id:
        return set()
    conn = get_db_connection()
    try:
        rows = select_all(conn, """
            SELECT course_id
            FROM enrollments
            WHERE user_id = %s
        """, (user_id,))
        ids = set()
        for row in rows or []:
            if isinstance(row, dict):
                ids.add(int(row["course_id"]))
            else:
                ids.add(int(row[0]))
        return ids
    except Exception as e:
        print("ERROR fetching enrolled course ids:", e)
        return set()
    finally:
        conn.close()


def _course_description_text(course):
    """Prefer DB description, then content.overview / summary fields."""
    desc = (course.get("description") or "").strip()
    if desc:
        return desc

    content = course.get("content") or {}
    if not isinstance(content, dict):
        content = {}

    for key in ("overview", "description", "summary"):
        value = content.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list):
            parts = [str(v).strip() for v in value if str(v).strip()]
            if parts:
                return " ".join(parts)

    outcomes = content.get("learning_outcomes")
    if isinstance(outcomes, list) and outcomes:
        return " ".join(str(o).strip() for o in outcomes[:3] if str(o).strip())

    return ""


def enrich_courses_for_discover(courses, enrolled_ids=None):
    """
    Attach description, rating, level, domain for discover cards.
    Drops courses the student already enrolled in (when enrolled_ids given).
    """
    enrolled_ids = enrolled_ids or set()
    enriched = []

    for course in courses or []:
        course_id = course.get("id")
        if course_id is None:
            continue
        try:
            course_id = int(course_id)
        except (TypeError, ValueError):
            continue

        if course_id in enrolled_ids:
            continue

        content = course.get("content") or {}
        if not isinstance(content, dict):
            content = {}

        description = _course_description_text(course)
        rating = get_course_rating_summary(course_id)

        course["id"] = course_id
        course["description"] = description
        course["overview"] = description
        course["rating"] = rating
        course["level"] = content.get("level") or course.get("level") or "All levels"
        course["domain"] = content.get("domain") or course.get("domain") or ""
        course["enrolled"] = False  # filtered list is not enrolled
        enriched.append(course)

    return enriched


def get_all_courses(user_id=None):
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
            SELECT id, title, description, content, popularity_score
            FROM courses
            WHERE is_public = 1
            ORDER BY created_at DESC
        """)
        courses = normalize_courses(courses)
        enrolled_ids = get_enrolled_course_ids(user_id) if user_id else set()
        return enrich_courses_for_discover(courses, enrolled_ids=enrolled_ids)

    except Exception as e:
        print("ERROR fetching courses:", e)
        return []

    finally:
        conn.close()


def _preference_keywords(user_id):
    """Build match keywords from learner preferences + recent searches."""
    keywords = []
    try:
        from app.services.profile_service import get_user_preferences, get_user_search_logs
        prefs = get_user_preferences(user_id) or {}
        domain = prefs.get("domain")
        if isinstance(domain, list):
            keywords.extend([str(d).strip() for d in domain if str(d).strip()])
        elif isinstance(domain, str) and domain.strip():
            # may be JSON string or plain text
            try:
                parsed = json.loads(domain)
                if isinstance(parsed, list):
                    keywords.extend([str(d).strip() for d in parsed if str(d).strip()])
                else:
                    keywords.append(domain.strip())
            except Exception:
                keywords.append(domain.strip())

        for key in ("topic", "goal", "level", "preferred_domains"):
            value = prefs.get(key)
            if isinstance(value, str) and value.strip():
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        keywords.extend([str(v).strip() for v in parsed if str(v).strip()])
                    else:
                        keywords.append(value.strip())
                except Exception:
                    keywords.append(value.strip())

        searches = get_user_search_logs(user_id) or []
        for row in searches[:8]:
            q = row.get("query") if isinstance(row, dict) else (row[0] if row else None)
            if q and str(q).strip():
                keywords.append(str(q).strip())
    except Exception as e:
        print("ERROR building preference keywords:", e)

    # de-dupe case-insensitively, keep order
    seen = set()
    unique = []
    for kw in keywords:
        key = kw.lower()
        if key and key not in seen and len(key) > 1:
            seen.add(key)
            unique.append(kw)
    return unique


def get_recommended_courses(user_id, limit=6):
    """
    Courses matching the learner's profile preferences that they have NOT enrolled in.
    Enrollment is once — enrolled courses never appear in Discover recommendations.
    """
    conn = get_db_connection()
    try:
        enrolled_ids = get_enrolled_course_ids(user_id)
        courses = select_all(conn, """
            SELECT id, title, description, content, popularity_score, created_at
            FROM courses
            WHERE is_public = 1
            ORDER BY created_at DESC
        """)
        courses = normalize_courses(courses)
        courses = enrich_courses_for_discover(courses, enrolled_ids=enrolled_ids)

        keywords = _preference_keywords(user_id)
        if not keywords:
            # No prefs yet: surface popular unenrolled courses as soft recommendations
            courses.sort(key=lambda c: (c.get("popularity_score") or 0), reverse=True)
            return courses[:limit]

        scored = []
        for course in courses:
            haystack = " ".join([
                str(course.get("title") or ""),
                str(course.get("description") or ""),
                str(course.get("domain") or ""),
                str(course.get("level") or ""),
                json.dumps(course.get("content") or {}, ensure_ascii=False),
            ]).lower()

            score = 0
            for kw in keywords:
                token = kw.lower()
                if token in haystack:
                    score += 3
                # partial token match for multi-word prefs
                for part in token.replace(",", " ").split():
                    if len(part) > 2 and part in haystack:
                        score += 1

            if score > 0:
                scored.append((score, course.get("popularity_score") or 0, course))

        if scored:
            scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
            return [item[2] for item in scored[:limit]]

        # Prefs exist but no keyword hits — still show unenrolled popular courses
        courses.sort(key=lambda c: (c.get("popularity_score") or 0), reverse=True)
        return courses[:limit]

    except Exception as e:
        print("ERROR fetching recommended courses:", e)
        return []

    finally:
        conn.close()


def get_trending_courses(user_id=None, limit=6):
    """
    Popular public courses the learner has NOT enrolled in.
    Trending is popularity-based, not limited to already-enrolled preference matches.
    """
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
            SELECT id, title, description, content, popularity_score, created_at
            FROM courses
            WHERE is_public = 1
            ORDER BY popularity_score DESC, created_at DESC
        """)
        courses = normalize_courses(courses)
        enrolled_ids = get_enrolled_course_ids(user_id) if user_id else set()
        courses = enrich_courses_for_discover(courses, enrolled_ids=enrolled_ids)
        return courses[:limit]

    except Exception as e:
        print("ERROR fetching trending courses:", e)
        return []

    finally:
        conn.close()


def log_search(user_id, query):
    conn = get_db_connection()
    try:
        insert(conn, """
            INSERT INTO search_logs (user_id, query)
            VALUES (%s, %s)
        """, (user_id, query))
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("ERROR logging search:", e)

    finally:
        conn.close()


def search_courses(query, user_id=None):
    """Search public courses; hide ones the student already enrolled in."""
    conn = get_db_connection()
    try:
        like = f"%{query}%"
        courses = select_all(conn, """
            SELECT id, title, description, content, popularity_score,
            CASE
                WHEN title LIKE %s THEN 1
                WHEN content LIKE %s THEN 2
                WHEN description LIKE %s THEN 2
                ELSE 3
            END as rank_score
            FROM courses
            WHERE is_public = 1
              AND (title LIKE %s OR content LIKE %s OR IFNULL(description, '') LIKE %s)
            ORDER BY rank_score ASC, popularity_score DESC
        """, (like, like, like, like, like, like))
        courses = normalize_courses(courses)
        enrolled_ids = get_enrolled_course_ids(user_id) if user_id else set()
        return enrich_courses_for_discover(courses, enrolled_ids=enrolled_ids)

    finally:
        conn.close()


def get_user_search_history(user_id):
    conn = get_db_connection()
    try:
        searches = select_all(conn, """
            SELECT query, created_at
            FROM search_logs
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        return [{"query": s[0], "timestamp": s[1]} for s in searches]

    except Exception as e:
        print("ERROR fetching search history:", e)
        return []

    finally:
        conn.close()
def get_user_enrollments(user_id):
    conn = get_db_connection()
    try:
        enrollments = select_all(conn, """
            SELECT c.id, c.title
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.user_id = %s
        """, (user_id,))
        return [{"course_id": e[0], "title": e[1]} for e in enrollments]

    except Exception as e:
        print("ERROR fetching enrollments:", e)
        return []

    finally:
        conn.close()
def get_user_reactions(user_id):
    conn = get_db_connection()
    try:
        reactions = select_all(conn, """
            SELECT reaction, COUNT(*) as count
            FROM course_feedback
            WHERE user_id = %s
            GROUP BY reaction
        """, (user_id,))
        return {r[0]: r[1] for r in reactions}

    except Exception as e:
        print("ERROR fetching reactions:", e)
        return {"likes": 0, "dislikes": 0}

    finally:
        conn.close()
def build_generation_context(student_id, topic):

    search_history = get_user_search_history(student_id)
    enrolled_courses = get_user_enrollments(student_id)
    reactions = get_user_reactions(student_id)

    return {
        "requested_topic": topic,
        "past_searches": search_history,
        "enrolled_topics": enrolled_courses,
        "liked_topics": reactions["likes"],
        "disliked_topics": reactions["dislikes"]
    }


import json


def normalize_courses(courses):
    for course in courses:
        raw_content = course.get("content")

        # Only parse if it's a string
        if isinstance(raw_content, str):
            try:
                course["content"] = json.loads(raw_content)
            except json.JSONDecodeError:
                course["content"] = {}

        # If it's already a dict, leave it alone
        elif isinstance(raw_content, dict):
            pass

        else:
            course["content"] = {}

    return courses



# eleven labs
# methods.py


# ✅ Helper function (place near top or with other helpers)
def split_text(text, chunk_size=1000):
    chunks = []
    while len(text) > chunk_size:
        split_index = text.rfind(' ', 0, chunk_size)
        if split_index == -1:
            split_index = chunk_size
        chunks.append(text[:split_index])
        text = text[split_index:]
    chunks.append(text)
    return chunks


# ✅ Main service function
def text_to_speech_service(text):
    if not text or len(text.strip()) == 0:
        raise ValueError("Text is empty")

    chunks = split_text(text)
    audio_segments = []

    for chunk in chunks:
        audio_segments.append(generate_speech(chunk))

    return b"".join(audio_segments)

# summary 



def summarize_service(text):
    if not text or len(text.strip()) == 0:
        raise ValueError("Text is empty")

    chunks = split_text(text)

    partial_summaries = []

    # 🔹 Step 1: summarize each chunk
    for chunk in chunks:
        prompt = f"Summarize this for a student in concise bullet points:\n{chunk}"
        partial_summaries.append(generate_summary(prompt))

    # 🔹 Step 2: combine summaries
    combined = "\n".join(partial_summaries)

    # 🔹 Step 3: final refinement (VERY IMPORTANT)
    final_prompt = f"""
    Combine and refine the following summaries into a clear, concise student-friendly summary:

    {combined}
    """

    final_summary = generate_summary(final_prompt)

    return final_summary



def explain_text_service(text, level="simple"):
    if not text or len(text.strip()) == 0:
        raise ValueError("Text is empty")

    # 🔥 Control explanation depth (important for LMS intelligence)
    level_map = {
        "simple": "Explain in very simple terms like teaching a beginner.",
        "medium": "Explain clearly with moderate detail.",
        "advanced": "Explain in a detailed and technical way."
    }

    instruction = level_map.get(level, level_map["simple"])

    prompt = f"""
    {instruction}

    Text:
    {text}

    Keep the explanation clear, structured, and easy to understand.
    """

    return generate_explanation(prompt)

# get marks for each lesson from db table lesson_quiz_results column score_percentage 
def get_lesson_quiz_score(user_id, course_id, module_index, lesson_index):
    conn = get_db_connection()
    try:
        result = select_one(conn, """
            SELECT score_percentage
            FROM lesson_quiz_results
            WHERE user_id = %s AND course_id = %s AND module_index = %s AND lesson_index = %s
        """, (user_id, course_id, module_index, lesson_index))

        return result[0] if result else None

    except Exception as e:
        print("ERROR fetching lesson quiz score:", e)
        return None

    finally:
        conn.close()

def get_module_quiz_average(user_id, course_id, module_index):
    conn = get_db_connection()
    try:
        result = select_one(conn, """
            SELECT AVG(score_percentage)
            FROM lesson_quiz_results
            WHERE user_id = %s AND course_id = %s AND module_index = %s
        """, (user_id, course_id, module_index))

        return result[0] if result and result[0] is not None else None

    except Exception as e:
        print("ERROR fetching module quiz average:", e)
        return None

    finally:
        conn.close()

def _parse_course_content(raw_content):
    """Normalize course content from MySQL (str/bytes/dict) into a dict."""
    if raw_content is None:
        return {}
    if isinstance(raw_content, (bytes, bytearray)):
        raw_content = raw_content.decode("utf-8", errors="ignore")
    if isinstance(raw_content, dict):
        return raw_content
    if isinstance(raw_content, str):
        try:
            return json.loads(raw_content)
        except Exception:
            return {}
    return {}


def is_module_completed(user_id, course_id, module_index, expected_lessons=None):
    """True only when every lesson quiz in the module has a result.

    Empty or unknown modules are NOT treated as completed.
    """
    conn = get_db_connection()
    try:
        if expected_lessons is None:
            course = select_one(conn, """
                SELECT content FROM courses WHERE id = %s
            """, (course_id,))

            if course and course[0]:
                course_content = _parse_course_content(course[0])
                modules = course_content.get("modules") or []
                if 0 <= module_index < len(modules):
                    expected_lessons = len((modules[module_index] or {}).get("lessons") or [])
                else:
                    expected_lessons = 0
            else:
                expected_lessons = 0

        if not expected_lessons or expected_lessons <= 0:
            return False

        result = select_one(conn, """
            SELECT COUNT(DISTINCT lesson_index)
            FROM lesson_quiz_results
            WHERE user_id = %s AND course_id = %s AND module_index = %s
        """, (user_id, course_id, module_index))

        completed_lessons = int(result[0]) if result and result[0] is not None else 0
        return completed_lessons >= expected_lessons

    except Exception as e:
        print(f"ERROR checking module completion for user {user_id}, course {course_id}, module {module_index}:", e)
        return False

    finally:
        conn.close()


def is_module_assessed(user_id, course_id, module_index):
    """True when the student has completed the module assessment."""
    conn = get_db_connection()
    try:
        result = select_one(conn, """
            SELECT completed
            FROM module_assessment_results
            WHERE user_id = %s AND course_id = %s AND module_index = %s
            LIMIT 1
        """, (user_id, course_id, module_index))
        if not result:
            return False
        return bool(result[0])
    except Exception as e:
        print(f"ERROR checking module assessment for user {user_id}, course {course_id}, module {module_index}:", e)
        return False
    finally:
        conn.close()


def count_completed_lessons(user_id, course_id):
    """Count lesson quizzes the student has finished for a course."""
    conn = get_db_connection()
    try:
        result = select_one(conn, """
            SELECT COUNT(DISTINCT CONCAT(module_index, ':', lesson_index))
            FROM lesson_quiz_results
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))
        return int(result[0]) if result and result[0] is not None else 0
    except Exception as e:
        print("ERROR counting completed lessons:", e)
        return 0
    finally:
        conn.close()


def get_course_rating_summary(course_id):
    """
    Student-facing course rating for social proof.
    Prefers expert/manual evaluations (0–5 stars), falls back to like ratio.
    """
    conn = get_db_connection()
    try:
        expert = select_one(conn, """
            SELECT AVG(score / NULLIF(max_score, 0) * 5), COUNT(*)
            FROM manual_evaluations
            WHERE course_id = %s
        """, (course_id,))

        likes_row = select_one(conn, """
            SELECT
                SUM(CASE WHEN reaction = 'like' THEN 1 ELSE 0 END),
                SUM(CASE WHEN reaction = 'dislike' THEN 1 ELSE 0 END),
                COUNT(*)
            FROM course_feedback
            WHERE course_id = %s
        """, (course_id,))

        enroll_row = select_one(conn, """
            SELECT COUNT(*) FROM enrollments WHERE course_id = %s
        """, (course_id,))

        pop_row = select_one(conn, """
            SELECT popularity_score FROM courses WHERE id = %s
        """, (course_id,))

        likes = int(likes_row[0] or 0) if likes_row else 0
        dislikes = int(likes_row[1] or 0) if likes_row else 0
        feedback_count = int(likes_row[2] or 0) if likes_row else 0
        enrollments = int(enroll_row[0] or 0) if enroll_row else 0
        popularity = int(pop_row[0] or 0) if pop_row else 0

        average = None
        count = 0
        source = None

        if expert and expert[0] is not None and int(expert[1] or 0) > 0:
            average = round(float(expert[0]), 1)
            count = int(expert[1])
            source = "expert"
        elif feedback_count > 0:
            # Map like ratio to a 1–5 scale (neutral baseline 3.0)
            ratio = likes / feedback_count
            average = round(1.0 + (ratio * 4.0), 1)
            count = feedback_count
            source = "community"

        return {
            "average": average,
            "count": count,
            "likes": likes,
            "dislikes": dislikes,
            "enrollments": enrollments,
            "popularity_score": popularity,
            "source": source,
            "has_rating": average is not None,
        }
    except Exception as e:
        print("ERROR fetching course rating summary:", e)
        return {
            "average": None,
            "count": 0,
            "likes": 0,
            "dislikes": 0,
            "enrollments": 0,
            "popularity_score": 0,
            "source": None,
            "has_rating": False,
        }
    finally:
        conn.close()


def ensure_course_instructor_column():
    """Add courses.instructor_id if missing (assistant instructor for the course)."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SHOW COLUMNS FROM courses LIKE 'instructor_id'")
        if not cur.fetchone():
            cur.execute("""
                ALTER TABLE courses
                ADD COLUMN instructor_id INT NULL,
                ADD KEY idx_course_instructor (instructor_id),
                ADD CONSTRAINT fk_course_instructor
                    FOREIGN KEY (instructor_id) REFERENCES users(id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            """)
            conn.commit()
        cur.close()
    except Exception as e:
        # Non-fatal if FK already exists under another name or privileges differ
        try:
            conn.rollback()
        except Exception:
            pass
        # Retry simple column add without FK
        try:
            cur = conn.cursor()
            cur.execute("SHOW COLUMNS FROM courses LIKE 'instructor_id'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE courses ADD COLUMN instructor_id INT NULL")
                conn.commit()
            cur.close()
        except Exception as e2:
            print("ERROR ensuring instructor_id column:", e2)
    finally:
        conn.close()


def _tokenize(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip().lower() for v in value if str(v).strip()]
    if isinstance(value, dict):
        return [str(v).strip().lower() for v in value.values() if str(v).strip()]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(v).strip().lower() for v in parsed if str(v).strip()]
    except Exception:
        pass
    # comma / slash / pipe separated expertise
    parts = []
    for chunk in text.replace("/", ",").replace("|", ",").replace(";", ",").split(","):
        if chunk.strip():
            parts.append(chunk.strip().lower())
    return parts or [text.lower()]


def _course_domain_and_duration(content):
    """Extract domain label and duration months from course content JSON."""
    if isinstance(content, (bytes, bytearray)):
        content = content.decode("utf-8", errors="ignore")
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception:
            content = {}
    if not isinstance(content, dict):
        content = {}

    domain = content.get("domain")
    if isinstance(domain, list):
        domain = domain[0] if domain else ""
    domain = str(domain or "").strip()

    duration = content.get("duration")
    if duration is None:
        duration = content.get("duration_months") or content.get("length")
    # normalize display
    if duration is None or duration == "":
        duration_display = None
        duration_value = None
    else:
        duration_value = duration
        duration_display = f"{duration} months" if str(duration).replace(".", "", 1).isdigit() else str(duration)

    return domain, duration_value, duration_display, content


def list_available_instructors():
    """Instructors (and admins with expertise) who can support courses."""
    conn = get_db_connection()
    try:
        rows = select_all(conn, """
            SELECT id, full_name, email, role, expertise_domain
            FROM users
            WHERE role = 'instructor'
               OR (role = 'admin' AND expertise_domain IS NOT NULL AND expertise_domain != '')
            ORDER BY full_name ASC
        """)
        instructors = []
        for row in rows or []:
            if isinstance(row, dict):
                instructors.append({
                    "id": int(row["id"]),
                    "full_name": row.get("full_name") or "Instructor",
                    "email": row.get("email"),
                    "role": row.get("role"),
                    "expertise_domain": row.get("expertise_domain") or "",
                    "expertise_tokens": _tokenize(row.get("expertise_domain")),
                })
            else:
                instructors.append({
                    "id": int(row[0]),
                    "full_name": row[1] or "Instructor",
                    "email": row[2],
                    "role": row[3],
                    "expertise_domain": row[4] or "",
                    "expertise_tokens": _tokenize(row[4]),
                })
        return instructors
    except Exception as e:
        print("ERROR listing instructors:", e)
        return []
    finally:
        conn.close()


def _instructor_match_score(instructor, course_domain, title, content):
    """Higher score = better expertise fit for the course."""
    haystack_parts = [
        str(course_domain or ""),
        str(title or ""),
    ]
    if isinstance(content, dict):
        for key in ("domain", "overview", "title", "target_audience", "prerequisites"):
            haystack_parts.append(str(content.get(key) or ""))
        outcomes = content.get("learning_outcomes") or []
        if isinstance(outcomes, list):
            haystack_parts.extend(str(o) for o in outcomes[:8])
    haystack = " ".join(haystack_parts).lower()

    score = 0
    tokens = instructor.get("expertise_tokens") or []
    if not tokens:
        # Prefer named instructors without expertise over nothing, but rank last
        return 0

    for token in tokens:
        if not token or len(token) < 2:
            continue
        if token in haystack:
            score += 10
        # partial word hits
        for part in token.split():
            if len(part) > 3 and part in haystack:
                score += 3

    # Prefer pure instructors over admins when scores tie (handled outside)
    if (instructor.get("role") or "").lower() == "instructor":
        score += 0.5
    return score


def assign_course_instructor(course_id, force=False):
    """
    Assign an assistant instructor based on expertise vs course domain/content.
    Persists courses.instructor_id. Returns instructor dict or None.
    """
    ensure_course_instructor_column()
    conn = get_db_connection()
    try:
        row = select_one(conn, """
            SELECT id, title, content, instructor_id
            FROM courses
            WHERE id = %s
        """, (course_id,))
        if not row:
            return None

        existing_instructor_id = row[3]
        if existing_instructor_id and not force:
            # Return existing assignment details
            inst = select_one(conn, """
                SELECT id, full_name, email, expertise_domain
                FROM users WHERE id = %s
            """, (existing_instructor_id,))
            if inst:
                return {
                    "id": int(inst[0]),
                    "full_name": inst[1],
                    "email": inst[2],
                    "expertise_domain": inst[3] or "",
                }

        domain, _dur, _dur_disp, content = _course_domain_and_duration(row[2])
        title = row[1]
        instructors = list_available_instructors()
        if not instructors:
            return None

        ranked = sorted(
            instructors,
            key=lambda i: _instructor_match_score(i, domain, title, content),
            reverse=True,
        )
        best = ranked[0]
        best_score = _instructor_match_score(best, domain, title, content)

        # If no expertise match, pick least-loaded instructor (workload balance)
        if best_score < 1:
            load_rows = select_all(conn, """
                SELECT instructor_id, COUNT(*) AS cnt
                FROM courses
                WHERE instructor_id IS NOT NULL
                GROUP BY instructor_id
            """) or []
            load = {}
            for lr in load_rows:
                if isinstance(lr, dict):
                    load[int(lr["instructor_id"])] = int(lr["cnt"] or 0)
                else:
                    load[int(lr[0])] = int(lr[1] or 0)
            pure = [i for i in instructors if (i.get("role") or "").lower() == "instructor"] or instructors
            pure.sort(key=lambda i: (load.get(i["id"], 0), i.get("full_name") or ""))
            best = pure[0]

        update(conn, """
            UPDATE courses SET instructor_id = %s WHERE id = %s
        """, (best["id"], course_id))

        return {
            "id": best["id"],
            "full_name": best.get("full_name"),
            "email": best.get("email"),
            "expertise_domain": best.get("expertise_domain") or "",
        }
    except Exception as e:
        print(f"ERROR assigning instructor for course {course_id}:", e)
        return None
    finally:
        conn.close()


def get_course_instructor(course_id):
    """Return assigned instructor for a course (assign if missing)."""
    ensure_course_instructor_column()
    conn = get_db_connection()
    try:
        row = select_one(conn, """
            SELECT c.instructor_id, u.full_name, u.email, u.expertise_domain
            FROM courses c
            LEFT JOIN users u ON u.id = c.instructor_id
            WHERE c.id = %s
        """, (course_id,))
        if row and row[0]:
            return {
                "id": int(row[0]),
                "full_name": row[1] or "Instructor",
                "email": row[2],
                "expertise_domain": row[3] or "",
            }
    except Exception as e:
        print("ERROR get_course_instructor:", e)
    finally:
        conn.close()
    return assign_course_instructor(course_id)


def get_public_catalog_courses(user_id=None):
    """
    Public catalog for /courses: description, duration, rating, likes,
    enrollment count, and assigned assistant instructor.
    """
    ensure_course_instructor_column()
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
            SELECT c.id, c.title, c.description, c.content, c.popularity_score,
                   c.created_at, c.instructor_id,
                   u.full_name AS instructor_name,
                   u.email AS instructor_email,
                   u.expertise_domain AS instructor_expertise
            FROM courses c
            LEFT JOIN users u ON u.id = c.instructor_id
            WHERE c.is_public = 1
            ORDER BY c.popularity_score DESC, c.created_at DESC
        """) or []

        enrolled_ids = set()
        if user_id:
            enrolled_ids = get_enrolled_course_ids(user_id)

        catalog = []
        for row in courses:
            if isinstance(row, dict):
                course_id = int(row["id"])
                title = row.get("title")
                description = (row.get("description") or "").strip()
                content_raw = row.get("content")
                popularity = row.get("popularity_score") or 0
                created_at = row.get("created_at")
                instructor_id = row.get("instructor_id")
                instructor_name = row.get("instructor_name")
                instructor_email = row.get("instructor_email")
                instructor_expertise = row.get("instructor_expertise") or ""
            else:
                course_id = int(row[0])
                title = row[1]
                description = (row[2] or "").strip()
                content_raw = row[3]
                popularity = row[4] or 0
                created_at = row[5]
                instructor_id = row[6]
                instructor_name = row[7]
                instructor_email = row[8]
                instructor_expertise = row[9] or ""

            domain, duration_value, duration_display, content = _course_domain_and_duration(content_raw)
            if not description:
                description = (
                    (content.get("overview") or content.get("description") or "")
                    if isinstance(content, dict) else ""
                )
                if isinstance(description, list):
                    description = " ".join(str(x) for x in description[:3])

            instructor = None
            if instructor_id and instructor_name:
                instructor = {
                    "id": int(instructor_id),
                    "full_name": instructor_name,
                    "email": instructor_email,
                    "expertise_domain": instructor_expertise,
                }
            else:
                instructor = assign_course_instructor(course_id)

            rating = get_course_rating_summary(course_id)
            reaction = get_user_reaction(user_id, course_id) if user_id else None

            catalog.append({
                "id": course_id,
                "title": title,
                "description": description or "",
                "domain": domain or (content.get("domain") if isinstance(content, dict) else "") or "",
                "level": (content.get("level") if isinstance(content, dict) else None) or "All levels",
                "duration": duration_value,
                "duration_display": duration_display or "Flexible",
                "popularity_score": popularity,
                "created_at": created_at,
                "rating": rating,
                "likes": rating.get("likes", 0),
                "dislikes": rating.get("dislikes", 0),
                "enrollments": rating.get("enrollments", 0),
                "instructor": instructor,
                "reaction": reaction,
                "enrolled": course_id in enrolled_ids,
            })

        return catalog
    except Exception as e:
        print("ERROR building public catalog:", e)
        traceback_msg = e
        print(traceback_msg)
        return []
    finally:
        conn.close()


def get_certificate_if_earned(user_id, course_id):
    conn = get_db_connection()
    try:
        certificate = select_one(conn, """
            SELECT certificate_url
            FROM certificates
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

        return certificate[0] if certificate else None

    except Exception as e:
        print("ERROR fetching certificate:", e)
        return None

    finally:
        conn.close()

def existing_certificate(user_id, course_id):
    conn = get_db_connection()
    try:
        certificate = select_one(conn, """
            SELECT certificate_url
            FROM certificates
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

        return certificate[0] if certificate else None

    except Exception as e:
        print("ERROR checking existing certificate:", e)
        return None

    finally:
        conn.close()

def save_certificate(user_id, course_id, certificate_code, certificate_url):
    conn = get_db_connection()
    try:
        existing = existing_certificate(user_id, course_id)
        if existing:
            update(conn, """
                UPDATE certificates
                SET certificate_url = %s, created_at = NOW()
                WHERE user_id = %s AND course_id = %s
            """, (certificate_url, user_id, course_id))
        else:
            insert(conn, """
                INSERT INTO certificates (user_id, course_id,certificate_code, issue_date, certificate_url)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (user_id, course_id, certificate_code, certificate_url))
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("ERROR saving certificate:", e)

    finally:
        conn.close()