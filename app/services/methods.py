from flask import request, session, redirect, url_for, flash
from app.db_management.sql import select_one, insert, update, select_all
from app.db_management.db import get_db_connection
from app.services.profile_service import build_user_profile
import hashlib
import json

def get_current_user_profile():
    if "user_id" not in session:
        return None
    return build_user_profile(session["user_id"])
def save_course_reaction():

    conn = get_db_connection()

    try:
        # 1️⃣ Ensure user logged in
        if "user_id" not in session:
            return "Unauthorized", 401

        user_id = session["user_id"]
        reaction = request.form.get("action")
        course_data = session.get("generated_course")

        if not course_data:
            return "No course data found.", 400

        if reaction not in ["like", "dislike"]:
            return "Invalid reaction.", 400

        # 2️⃣ Generate content hash
        content_hash = hashlib.sha256(
            json.dumps(course_data, sort_keys=True).encode("utf-8")
        ).hexdigest()

        # 3️⃣ Check if course already exists
        course = select_one(conn, """
            SELECT id
            FROM courses
            WHERE content_hash = %s
        """, (content_hash,))

        if course:
            course_id = course[0]
        else:
            # Insert course
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
                course_data.get("description", ""),
                json.dumps(course_data),
                content_hash,
                json.dumps(course_data.get("preferences", {})),
                user_id
            ))

            # 🔥 Immediately fetch the inserted course
            course = select_one(conn, """
                SELECT id
                FROM courses
                WHERE content_hash = %s
            """, (content_hash,))

            if not course:
                raise Exception("Course insert failed — could not retrieve ID.")

            course_id = course[0]

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

        flash("Reaction saved successfully.", "success")
        return redirect(url_for("main.view_course", course_id=course_id))

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
def get_all_courses():
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
            SELECT id, title, description, popularity_score
            FROM courses
            WHERE is_public = 1
            ORDER BY created_at DESC
        """)
        courses = normalize_courses(courses)
        return courses

    except Exception as e:
        print("ERROR fetching courses:", e)
        return []

    finally:
        conn.close()

#get_recommended_courses, get_trending_courses, log_search, search_courses
def get_recommended_courses(user_id):
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
            SELECT c.id, c.title, c.description, c.popularity_score
            FROM courses c
            JOIN course_feedback f ON c.id = f.course_id
            WHERE f.user_id = %s AND f.reaction = 'like' AND c.is_public = 1
            ORDER BY c.created_at DESC
            LIMIT 5
        """, (user_id,))
        courses = normalize_courses(courses)
        return courses

    except Exception as e:
        print("ERROR fetching recommended courses:", e)
        return []

    finally:
        conn.close()
def get_trending_courses():
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
            SELECT id, title, description, popularity_score
            FROM courses
            WHERE is_public = 1
            ORDER BY popularity_score DESC, created_at DESC
            LIMIT 5
        """)
        courses = normalize_courses(courses)
        return courses

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
import json

def search_courses(query):
    conn = get_db_connection()
    try:
        courses = select_all(conn, """
        SELECT *,
        CASE
            WHEN title LIKE %s THEN 1
            WHEN content LIKE %s THEN 2
            ELSE 3
        END as rank_score
        FROM courses
        WHERE title LIKE %s OR content LIKE %s
        ORDER BY rank_score ASC, popularity_score DESC
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        courses = normalize_courses(courses)



        return courses

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