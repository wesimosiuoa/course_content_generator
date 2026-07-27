from app.db_management.db import *
from app.db_management.sql import *

import json

def get_user_preferences(user_id, check_complete=False):
    """
    Get user preferences.
    
    Args:
        user_id: The user ID
        check_complete: If True, only returns preferences if ALL required fields are present
    
    Returns:
        dict with preferences or None if not found/incomplete
    """
    conn = get_db_connection()
    result = select_all(conn,
        """SELECT id, user_id, domain, topic, goal, level, duration, 
                  learning_preference, prior_knowledge 
           FROM user_preferences 
           WHERE user_id = %s""",
        (user_id,)
    )

    if not result:
        return None

    pref = result[0]

    # Convert domains JSON string → Python list
    if pref["domain"]:
        try:
            pref["domain"] = json.loads(pref["domain"])
        except:
            pref["domain"] = []
    else:
        pref["domain"] = []

    # If checking for completeness, verify essential fields exist
    if check_complete:
        # Only check for domain (must have at least one item) and topic
        if not pref.get("domain") or (isinstance(pref["domain"], list) and len(pref["domain"]) == 0):
            return None
        if not pref.get("topic") or pref["topic"].strip() == "":
            return None

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
    preferences = get_user_preferences(user_id) or {}
    searches = get_user_search_logs(user_id) or []
    enrollments = get_user_enrollments(user_id) or []
    reactions = get_user_reactions(user_id) or []

    liked_ids = [r["course_id"] for r in reactions if r["reaction"] == "like"]
    disliked_ids = [r["course_id"] for r in reactions if r["reaction"] == "dislike"]
    enrolled_ids = [e["course_id"] for e in enrollments]

    enrolled_domains = get_course_domains(enrolled_ids)
    liked_domains = get_course_domains(liked_ids)

    search_queries = [s["query"] for s in searches]

    interest_scores = compute_interest_scores(
        search_queries,
        enrolled_domains,
        liked_domains
    )

    engagement_score = calculate_engagement(
        liked_ids,
        enrolled_ids,
        search_queries
    )

    estimated_level = estimate_level(
        preferences.get("level"),
        len(enrolled_ids)
    )

    return {
        "user_id": user_id,
        "static_profile": {
            "preferred_domains": preferences.get("domain", []),
            "explicit_level": preferences.get("level", "Beginner")
        },
        "behavioral_profile": {
            "interest_scores": interest_scores,
            "liked_courses": liked_ids,
            "disliked_courses": disliked_ids,
            "recent_searches": search_queries
        },
        "derived_metrics": {
            "estimated_level": estimated_level,
            "engagement_score": engagement_score
        }
    }
import json


def save_user_preferences(user_id, data):
    conn = get_db_connection()

    query = """
        INSERT INTO user_preferences 
        (user_id, domain, topic, goal, level, duration, learning_preference, prior_knowledge)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            domain = VALUES(domain),
            topic = VALUES(topic),
            goal = VALUES(goal),
            level = VALUES(level),
            duration = VALUES(duration),
            learning_preference = VALUES(learning_preference),
            prior_knowledge = VALUES(prior_knowledge)
    """

    insert(conn, query, (
        user_id,
        data["domain"],
        data["topic"],
        data["goal"],
        data["level"],
        data["duration"],
        data["learning_preference"],
        data["prior_knowledge"]
    ))

    conn.close()

def calculate_engagement(likes, enrollments, searches):
    return (len(likes) * 3) + (len(enrollments) * 2) + len(searches)

def estimate_level(preferred_level, enrollments_count):
    if enrollments_count >= 6:
        return "Advanced"
    elif enrollments_count >= 3:
        return "Intermediate"
    return preferred_level or "Beginner"

def get_course_domains(course_ids):
    if not course_ids:
        return []

    conn = get_db_connection()
    format_strings = ','.join(['%s'] * len(course_ids))

    query = f"""
        SELECT JSON_UNQUOTE(JSON_EXTRACT(content, '$.domain')) AS domain
        FROM courses
        WHERE id IN ({format_strings})
    """

    results = select_all(conn, query, tuple(course_ids))
    conn.close()

    return [r["domain"] for r in results if r["domain"]]

from collections import Counter

def compute_interest_scores(searches, enrolled_domains, liked_domains):
    score = Counter()

    for s in searches:
        score[s] += 1

    for d in enrolled_domains:
        score[d] += 2

    for d in liked_domains:
        score[d] += 3

    return dict(score)