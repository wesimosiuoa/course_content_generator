

from flask import Blueprint, abort, jsonify, render_template, request, redirect, url_for, flash, session
import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.message import message
import json
import hashlib
from .db_management.db import get_db_connection
from .db_management.sql import insert as db_insert
from .db_management.sql import select as db_select
from .db_management.sql import update as db_update
from .db_management.sql import delete as db_delete
from .db_management.sql import select_one as db_select_one
from .services.methods import get_current_user_profile, save_course_reaction, is_enrolled, get_user_reaction, get_all_courses, get_recommended_courses, get_trending_courses, log_search, search_courses
from app.services.profile_service import *
# LLM API token and URL for LLM service
from app.services.llm_service import generate_course



main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')



@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        next_page = request.args.get("next")
        return render_template('login.html', next_page=next_page)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        next_page = request.form.get("next_page")  # 👈 IMPORTANT

        conn = get_db_connection()

        try:
            user = db_select_one(conn, """
                SELECT id, full_name, email, password_hash
                FROM users
                WHERE email = %s
            """, (email,))

            if user and check_password_hash(user[3], password):

                session['user_id'] = user[0]
                session['full_name'] = user[1]
                session['email'] = user[2]

                profile = get_current_user_profile()
                session["profile_level"] = profile["level"]

                pref = get_user_preferences(user[0])

                if not pref:
                    return redirect("/set_preferences")

                flash("Login successful!", "success")

                if next_page and next_page not in ("None", "", None):
                    return redirect(next_page)

                return redirect(url_for("main.student_dashboard"))
            else:
                flash("Invalid email or password.", "danger")

        except Exception as e:
            print (f" Error from db {str(e)}")
            flash("Database error occurred.", "danger")

        finally:
            conn.close()

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            
            db_insert(conn, """
                INSERT INTO users (full_name, email, password_hash)
                VALUES (%s, %s, %s)
            """, (full_name, email, password_hash))
            conn.commit()

            message("Account created successfully!", "success")
            return redirect(url_for('main.login'))

        except mysql.connector.Error as err:
            message("Email already exists.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@main.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session:
        message("Please log in to access the dashboard.", "warning")
        return redirect(url_for('main.login'))

    return render_template('/student/student_dashboard.html', full_name=session.get('full_name'))

@main.route('/preferences')
def preferences():
    return render_template('preference.html')
@main.route('/generate_preview', methods=['POST', 'GET'])
def generate_preview():

    preferences = {
        "domain": request.form.get("domain"),
        "topic": request.form.get("topic"),
        "goal": request.form.get("goal"),
        "level": request.form.get("level"),
        "duration": request.form.get("duration"),
        "learning_preference": request.form.get("learning_preference"),
        "prior_knowledge": request.form.get("prior_knowledge")
    }

    try:
        if not preferences["domain"] or not preferences["topic"]:
            flash("Domain and Topic are required fields.", "danger")
            return redirect(url_for("main.preferences"))

        course_data = generate_course(preferences)
        session["generated_course"] = course_data
        session["preferences"] = preferences
        print("Generated Course Data:", course_data)
        print (f'course in session: {session["generated_course"]} and preferences: {session["preferences"]}')
        

        if not course_data:
            flash("Course generation failed. Please try again.", "danger")
            return redirect(url_for("main.preferences"))

    except Exception as e:
        print("Error during course generation:", str(e))
        flash("An error occurred during course generation.", "danger")
        return redirect(url_for("main.preferences"))

    return render_template("preview.html", course=course_data)

@main.route('/react_course', methods=['POST'])
def react_course():

    if "user_id" not in session:
        flash("Please log in to react to this course.", "warning")

        next_page = request.form.get("next_page")

        print("NEXT PAGE FROM FORM:", next_page)  # debug

        return redirect(url_for("main.login", next=next_page))

    return save_course_reaction()

@main.route("/courses")
def courses():

    conn = get_db_connection()

    try:
        courses = db_select(conn, """
            SELECT id, title, description, popularity_score, created_at
            FROM courses
            WHERE is_public = 1
            ORDER BY popularity_score DESC, created_at DESC
        """)

        formatted_courses = []

        for course in courses:
            formatted_courses.append({
                "id": course[0],
                "title": course[1],
                "description": course[2],
                "popularity_score": course[3],
                "created_at": course[4]
            })

        # ✅ ADD THIS BLOCK HERE
        if "user_id" in session:
            enrolled_courses = db_select(conn, """
                SELECT course_id FROM enrollments
                WHERE user_id = %s
            """, (session["user_id"],))

            enrolled_ids = {row[0] for row in enrolled_courses}
        else:
            enrolled_ids = set()

        reaction = get_user_reaction(session.get("user_id"), enrolled_ids["id"]) if "user_id" in session else None
        print("User reaction for course:", reaction)  # debug
        enrolled = is_enrolled(session.get("user_id"), enrolled_ids["id"]) if "user_id" in session else False
        return render_template(
            "courses.html",
            courses=formatted_courses,
            reaction=reaction,
            enrolled=enrolled
        )

    finally:
        conn.close()

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


@main.route("/course/<int:course_id>")
def view_course(course_id):

    conn = get_db_connection()

    try:
        # 1️⃣ Fetch course
        course = db_select_one(conn, """
            SELECT id, title, description, content, popularity_score, created_at
            FROM courses
            WHERE id = %s
        """, (course_id,))

        if not course:
            abort(404)

        # 2️⃣ Unpack
        course_data = {
            "id": course[0],
            "title": course[1],
            "description": course[2],
            "content": json.loads(course[3]),
            "popularity_score": course[4],
            "created_at": course[5]
        }

        # 3️⃣ Check if logged-in user reacted
        user_reaction = None

        if "user_id" in session:
            feedback = db_select_one(conn, """
                SELECT reaction
                FROM course_feedback
                WHERE user_id = %s AND course_id = %s
            """, (session["user_id"], course_id))

            if feedback:
                user_reaction = feedback[0]

        return render_template(
            "course_content.html",
            course=course_data,
            user_reaction=user_reaction
        )

    finally:
        conn.close()
# enrollment route
@main.route("/enroll/<int:course_id>")
def enroll(course_id):

    if "user_id" not in session:
        return redirect(url_for("main.login", next=url_for("main.enroll", course_id=course_id)))

    conn = get_db_connection()

    try:
        db_insert(conn, """
            INSERT IGNORE INTO enrollments (user_id, course_id)
            VALUES (%s, %s)
        """, (session["user_id"], course_id))

        flash("Successfully enrolled in course.", "success")

        return redirect(url_for("main.view_course", course_id=course_id))

    finally:
        conn.close()


@main.route("/my_courses")
def my_courses():

    if "user_id" not in session:
        return redirect(url_for("main.login", next=url_for("main.my_courses")))

    conn = get_db_connection()

    try:
        courses = db_select(conn, """
            SELECT c.id, c.title, c.content, c.popularity_score, c.created_at
            FROM courses c
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.user_id = %s
            ORDER BY e.enrolled_at DESC
        """, (session["user_id"],))

        formatted_courses = []

        for course in courses:
            formatted_courses.append({
                "id": course[0],
                "title": course[1],
                "overview": json.loads(course[2]).get("overview", ""),
                "popularity_score": course[3],
                "created_at": course[4]
            })

        return render_template("student/courses.html", courses=formatted_courses)

    finally:
        conn.close()


@main.route("/view_my_course/<int:course_id>")
def view_my_course(course_id):

    if "user_id" not in session:
        return redirect(url_for("main.login", next=url_for("main.view_my_course", course_id=course_id)))

    conn = get_db_connection()

    try:
        course = db_select_one(conn, """
            SELECT id, title, description, content, popularity_score, created_at
            FROM courses
            WHERE id = %s
        """, (course_id,))

        if not course:
            abort(404)

        course_data = {
            "id": course[0],
            "title": course[1],
            "description": course[2],
            "content": json.loads(course[3]),
            "popularity_score": course[4],
            "created_at": course[5]
        }
        reaction = get_user_reaction(session.get("user_id"), course_data["id"]) if "user_id" in session else None
        print("User reaction for course:", reaction)  # debug
        enrolled = is_enrolled(session.get("user_id"), course_data["id"]) if "user_id" in session else False

        return render_template("student/view_course.html", course=course_data, reaction=reaction, enrolled=enrolled)

    finally:
        conn.close()

@main.route('/enroll_course/<int:course_id>', methods=['POST', 'GET'])
def enroll_course(course_id):
    if "user_id" not in session:
        return redirect(url_for("main.login", next=url_for("main.enroll_course", course_id=course_id)))

    conn = get_db_connection()

    try:
        db_insert(conn, """
            INSERT IGNORE INTO enrollments (user_id, course_id)
            VALUES (%s, %s)
        """, (session["user_id"], course_id))

        flash("Successfully enrolled in course.", "success")

        return redirect(url_for("main.view_my_course", course_id=course_id))

    finally:
        conn.close()


@main.route('/discover')
def discover():

    if 'user_id' not in session:
        return redirect(url_for("main.login"))
    student_id = session['user_id']
    query = request.args.get('query', '').strip()

    existing_courses = get_all_courses()
    search_results = []
    recommended_courses = get_recommended_courses(student_id)
    trending_courses = get_trending_courses()
    

    if query:
        # Log search behavior
        log_search(student_id, query)

        # Intelligent search
        search_results = search_courses(query)
        reaction = get_user_reaction(session.get("user_id"), trending_courses[0]["id"]) if "user_id" in session and trending_courses else None
        print("User reaction for trending course:", reaction)  # debug
        enrolled = is_enrolled(session.get("user_id"), trending_courses[0]["id"]) if "user_id" in session and trending_courses else False

    return render_template(
        "student/discover.html",
        search_results=search_results,
        recommended_courses=recommended_courses,
        trending_courses=trending_courses,
        existing_courses=existing_courses,
        query=query, 
        reaction=reaction if query else None,
        enrolled=enrolled if query else None
    )
# discover course as a student where the course they are looking for is not available yet, so they can input their preferences and get a generated course preview. Note this, we are using search behavior to trigger the course generation flow, so we will have a search bar on the discover page where they can input their desired course topic, and if it does not exist in the database, we will redirect them to the preferences page with the topic pre-filled. 
@main.route('/search', methods=['POST'])
def search():

    topic = request.form.get("topic")

    if not topic:
        flash("Please enter a topic to search.", "warning")
        return redirect(url_for("main.discover"))

    conn = get_db_connection()

    try:
        course = db_select_one(conn, """
            SELECT id
            FROM courses
            WHERE JSON_EXTRACT(content, '$.topic') = %s
        """, (json.dumps(topic),))

        if course:
            return redirect(url_for("main.view_course", course_id=course[0]))
        else:
            flash("Course not found. Please provide your preferences to generate a course preview.", "info")
            return redirect(url_for("main.set_preferences", topic=topic))

    finally:
        conn.close()


# Profile Building 
@main.route("/set_preferences", methods=["GET", "POST"])
def set_preferences():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":

        level = request.form.get("level")
        domains = request.form.getlist("domains")

        save_user_preferences(user_id, level, domains)
        flash(" Your preferences saved ", "success")

        return redirect(url_for("main.student_dashboard"))

    existing = get_user_preferences(user_id)

    return render_template(
        "student/preferences.html",
        existing=existing
    )

#generate course from logged in student 
@main.route ("/generate_course", methods=["GET", "POST"])
def generate_course(): 

    user_preferences = []
    conn = get_db_connection()
    if request.method == "POST": 
        try:
            user_preferences = select_one(
            conn,
            "select * from user_preferences where user_id = %s;", session["user_id"])
        
            if user_preferences: 
                flash (" We got your preferences ", "success")
                print (f" Preferences found ")
            else :
                flash ("Sorry, boss, we could'nt get your preferences ", "danger")
                print (f" Preferences not found ")
        except Exception as err: 
            print (f"An error ", err)
        finally: 
            conn.close()

    return render_template(
        "student/personalised_course.html", 
        user_preferences = user_preferences
    )