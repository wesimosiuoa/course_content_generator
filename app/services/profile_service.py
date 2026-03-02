from app.db_management.db import *
from app.db_management.sql import *

import json

def get_user_preferences(user_id):
    conn = get_db_connection()
    result = select_all(conn,
        "SELECT level, preferred_domains FROM user_preferences WHERE user_id = %s",
        (user_id,)
    )

    if not result:
        return None

    pref = result[0]

    # Convert domains JSON string → Python list
    if pref["preferred_domains"]:
        try:
            pref["preferred_domains"] = json.loads(pref["preferred_domains"])
        except:
            pref["preferred_domains"] = []
    else:
        pref["preferred_domains"] = []

    return pref


def get_user_search_logs(user_id):
    conn = get_db_connection()
    return select_all(conn,
        "SELECT query FROM search_logs WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    )


def get_user_enrollments(user_id):
    conn = get_db_connection()
    return select_all(conn,
        "SELECT course_id FROM enrollments WHERE user_id = %s",
        (user_id,)
    )


def get_user_reactions(user_id):
    conn = get_db_connection()
    return select_all(conn, 
        "SELECT * FROM course_feedback WHERE user_id = %s",
        (user_id,)
    )


def build_user_profile(user_id):
    preferences = get_user_preferences(user_id)
    searches = get_user_search_logs(user_id)
    enrollments = get_user_enrollments(user_id)
    reactions = get_user_reactions(user_id)

    liked = [r["course_id"] for r in reactions if r["reaction"] == "like"]
    disliked = [r["course_id"] for r in reactions if r["reaction"] == "dislike"]

    return {
        "user_id": user_id,
        "level": preferences["level"] if preferences else "Beginner",
        "preferred_domains": preferences["preferred_domains"] if preferences else [],
        "recent_searches": [s["query"] for s in searches],
        "enrolled_course_ids": [e["course_id"] for e in enrollments],
        "liked_course_ids": liked,
        "disliked_course_ids": disliked
    }

import json


def save_user_preferences(user_id, level, domains):
    conn = get_db_connection()

    domains_json = json.dumps(domains)

    query = """
        INSERT INTO user_preferences (user_id, level, preferred_domains)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            level = VALUES(level),
            preferred_domains = VALUES(preferred_domains)
    """

    insert(conn, query, (user_id, level, domains_json))