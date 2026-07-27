"""
Assessment Routes - Handle quiz, SAQ, and final assessment endpoints
Includes LLM-based grading for essays and short answer questions
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from app.db_management.db import get_db_connection
from app.db_management.sql import select as db_select
from app.db_management.sql import select_one as db_select_one
from app.db_management.sql import update as db_update
import app.services.assessment_service as assessment_service
import traceback
import json

assessment = Blueprint('assessment', __name__, url_prefix='/assessment')


def _get_user_role():
    return session.get('role', 'student')


def _is_admin():
    return _get_user_role() == 'admin'


def _is_instructor():
    return _get_user_role() == 'instructor'


def _format_domain(domain_value):
    if isinstance(domain_value, list):
        return domain_value[0] if domain_value else None
    if isinstance(domain_value, dict):
        return None
    return domain_value


def _get_course_domain(course_id):
    conn = get_db_connection()
    try:
        course_row = db_select_one(conn,
            "SELECT content FROM courses WHERE id = %s",
            (course_id,)
        )
        if not course_row or not course_row[0]:
            return None

        course_content = json.loads(course_row[0])
        return _format_domain(course_content.get('domain'))
    finally:
        conn.close()


def _user_has_access_to_course(course_id):
    if _is_admin():
        return True
    if not _is_instructor():
        return False

    user_id = session.get('user_id')
    # Assigned assistant instructor always has access (reevaluation / consultancy)
    if user_id:
        conn = get_db_connection()
        try:
            assigned = db_select_one(conn, """
                SELECT instructor_id FROM courses WHERE id = %s
            """, (course_id,))
            if assigned and assigned[0] and int(assigned[0]) == int(user_id):
                return True
        except Exception:
            pass
        finally:
            conn.close()

    course_domain = _get_course_domain(course_id)
    if not course_domain:
        return False

    expertise = session.get('expertise_domain', '') or ''
    allowed_domains = [domain.strip().lower() for domain in expertise.split(',') if domain.strip()]
    course_domain_l = course_domain.strip().lower()
    if course_domain_l in allowed_domains:
        return True
    # Partial expertise match (e.g. "AI" vs "Artificial Intelligence")
    for domain in allowed_domains:
        if domain in course_domain_l or course_domain_l in domain:
            return True
    return False


def _get_user_expertise_domains():
    expertise = session.get('expertise_domain', '') or ''
    return [domain.strip().lower() for domain in expertise.split(',') if domain.strip()]


def _require_instructor_or_admin():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if not (_is_instructor() or _is_admin()):
        return jsonify({'error': 'Forbidden'}), 403
    return None


def _get_response_course_id(response_id, response_type):
    conn = get_db_connection()
    try:
        if response_type == 'saq':
            row = db_select_one(conn,
                "SELECT course_id FROM student_saq_responses WHERE id = %s",
                (response_id,)
            )
        elif response_type == 'final':
            row = db_select_one(conn,
                "SELECT course_id FROM student_final_responses WHERE id = %s",
                (response_id,)
            )
        else:
            return None

        return row[0] if row else None
    finally:
        conn.close()


@assessment.route('/instructor/reevaluation-requests', methods=['GET'])
def instructor_reevaluation_requests():
    """List pending SAQ reevaluation requests for instructors/admins."""
    auth_resp = _require_instructor_or_admin()
    if auth_resp:
        return auth_resp

    conn = get_db_connection()
    try:
        rows = db_select(conn, """
            SELECT r.id, r.response_id, r.user_id, r.reason, r.status, r.requested_at,
                   ssr.course_id, ssr.module_index, ssr.answer_text, ssr.score, ssr.feedback,
                   saq.question_text, saq.max_score, u.full_name, c.title
            FROM saq_reevaluation_requests r
            JOIN student_saq_responses ssr ON ssr.id = r.response_id
            JOIN short_answer_questions saq ON saq.id = ssr.saq_id
            JOIN users u ON u.id = r.user_id
            JOIN courses c ON c.id = ssr.course_id
            ORDER BY r.requested_at DESC
        """)

        requests = []
        for row in rows:
            course_id = row[6]
            if not _is_admin() and not _user_has_access_to_course(course_id):
                continue

            requests.append({
                'id': row[0],
                'response_id': row[1],
                'student_name': row[13],
                'course_title': row[14],
                'course_id': course_id,
                'module_index': row[7],
                'reason': row[3],
                'status': row[4],
                'requested_at': row[5].isoformat() if row[5] else None,
                'answer_text': row[8],
                'score': float(row[9]) if row[9] is not None else None,
                'feedback': row[10],
                'question_text': row[11],
                'max_score': row[12]
            })

        return render_template('instructor/reevaluation_requests.html', requests=requests)
    finally:
        conn.close()


@assessment.route('/instructor/reevaluation-requests/<int:request_id>/resolve', methods=['POST'])
def resolve_reevaluation_request(request_id):
    """Mark a reevaluation request as reviewed or declined."""
    auth_resp = _require_instructor_or_admin()
    if auth_resp:
        return auth_resp

    action = request.form.get('action', 'reviewed').lower()
    if action not in ['reviewed', 'declined']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('assessment.instructor_reevaluation_requests'))

    conn = get_db_connection()
    try:
        request_row = db_select_one(conn, """
            SELECT r.id, ssr.course_id
            FROM saq_reevaluation_requests r
            JOIN student_saq_responses ssr ON ssr.id = r.response_id
            WHERE r.id = %s
        """, (request_id,))

        if not request_row:
            flash('Reevaluation request not found.', 'warning')
            return redirect(url_for('assessment.instructor_reevaluation_requests'))

        course_id = request_row[1]
        if not _is_admin() and not _user_has_access_to_course(course_id):
            flash('You do not have access to this request.', 'danger')
            return redirect(url_for('assessment.instructor_reevaluation_requests'))

        db_update(conn, """
            UPDATE saq_reevaluation_requests
            SET status = %s, reviewed_at = NOW()
            WHERE id = %s
        """, (action, request_id))
        conn.commit()
        flash(f'Reevaluation request marked as {action}.', 'success')
        return redirect(url_for('assessment.instructor_reevaluation_requests'))
    except Exception as e:
        print(f"Error resolving reevaluation request: {str(e)}")
        conn.rollback()
        flash('Failed to update reevaluation request.', 'danger')
        return redirect(url_for('assessment.instructor_reevaluation_requests'))
    finally:
        conn.close()


# ==================== QUIZ ROUTES ====================

@assessment.route('/quiz/<int:course_id>/<int:module_index>/<int:lesson_index>', methods=['GET'])
def get_quiz(course_id, module_index, lesson_index):
    """Get quiz for a specific lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        
        # Get course title
        course = db_select_one(conn, """
            SELECT title, content
            FROM courses
            WHERE id = %s
        """, (course_id,))
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
            
        course_title = course[0]
        course_content = json.loads(course[1])
        
        # Get module and lesson names
        try:
            module = course_content['modules'][module_index]
            lesson = module['lessons'][lesson_index]
            
            module_title = module.get('title', f'Module {module_index + 1}')
            lesson_title = lesson.get('title', f'Lesson {lesson_index + 1}')
        except (IndexError, KeyError):
            return jsonify({'error': 'Module or lesson not found'}), 404
        
        conn.close()
        
        # Get quiz questions
        quiz_data = assessment_service.get_lesson_quiz(course_id, module_index, lesson_index)
        questions = quiz_data.get('questions', []) if isinstance(quiz_data, dict) else quiz_data
        
        return jsonify({
            'status': 'success',
            'data': {
                'course_id': course_id,
                'course_title': course_title,
                'module_index': module_index,
                'module_title': module_title,
                'lesson_index': lesson_index,
                'lesson_title': lesson_title,
                'questions': questions,
                'total_questions': len(questions)
            }
        })
    except Exception as e:
        print(f"Error fetching quiz: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to load quiz'}), 500


@assessment.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz responses"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        course_id = data['course_id']
        module_index = data['module_index']
        lesson_index = data['lesson_index']
        responses = data['responses']  # List of {question_id, selected_option_id}
        
        result = assessment_service.submit_quiz_response(
            user_id, course_id, module_index, lesson_index, responses
        )
        
        return jsonify({
            'status': 'success',
            'data': result,
            'message': 'Quiz submitted successfully'
        })
    except Exception as e:
        print(f"Error submitting quiz: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to submit quiz'}), 500


@assessment.route('/quiz/result/<int:course_id>/<int:module_index>/<int:lesson_index>', methods=['GET'])
def get_quiz_result(course_id, module_index, lesson_index):
    """Get quiz result for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        user_id = session['user_id']
        
        result = db_select_one(conn, """
            SELECT total_questions, correct_answers, score_percentage, passed, completed_at
            FROM lesson_quiz_results
            WHERE user_id = %s AND course_id = %s 
            AND module_index = %s AND lesson_index = %s
        """, (user_id, course_id, module_index, lesson_index))
        
        conn.close()
        
        if result:
            return jsonify({
                'status': 'success',
                'data': {
                    'total_questions': result[0],
                    'correct_answers': result[1],
                    'score_percentage': float(result[2]),
                    'passed': bool(result[3]),
                    'completed_at': result[4].isoformat() if result[4] else None
                }
            })
        else:
            return jsonify({'status': 'not_attempted', 'message': 'Quiz not yet attempted'})
    except Exception as e:
        print(f"Error fetching quiz result: {str(e)}")
        return jsonify({'error': 'Failed to load result'}), 500


# ==================== SHORT ANSWER QUESTION ROUTES ====================

@assessment.route('/saq/<int:course_id>/<int:module_index>', methods=['GET'])
def get_saqs(course_id, module_index):
    """Get short answer questions for a module"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        saqs = assessment_service.get_module_saqs(course_id, module_index)
        if not saqs:
            conn = get_db_connection()
            try:
                course = db_select_one(conn, """
                    SELECT content
                    FROM courses
                    WHERE id = %s
                """, (course_id,))
                if course:
                    course_content = json.loads(course[0])
                    module_data = None
                    try:
                        module_data = course_content['modules'][module_index]
                    except (IndexError, KeyError):
                        module_data = None

                    if module_data:
                        assessment_service.create_saq_for_module(course_id, module_index, module_data)
                        saqs = assessment_service.get_module_saqs(course_id, module_index)
            finally:
                conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'course_id': course_id,
                'module_index': module_index,
                'questions': saqs,
                'total_questions': len(saqs)
            }
        })
    except Exception as e:
        print(f"Error fetching SAQs: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to load questions'}), 500


@assessment.route('/saq/submit', methods=['POST'])
def submit_saq():
    """Submit one or more short answer question responses"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request payload'}), 400
        
        user_id = session['user_id']
        course_id = data.get('course_id')
        module_index = data.get('module_index')
        responses = data.get('responses') if data.get('responses') is not None else [data]

        results = []
        for response in responses:
            result = assessment_service.submit_saq_response(
                user_id,
                course_id,
                module_index,
                response['saq_id'],
                response['answer_text']
            )
            results.append(result)

        # Recalculate module assessment score after all responses are saved and graded
        module_score = assessment_service.calculate_module_assessment_score(
            user_id, course_id, module_index
        )
        
        return jsonify({
            'status': 'success',
            'data': results,
            'module_score': round(module_score, 2),
            'message': 'Answers submitted successfully'
        })
    except Exception as e:
        print(f"Error submitting SAQ: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to submit answer'}), 500


@assessment.route('/saq/reevaluate', methods=['POST'])
def request_saq_reevaluation():
    """Request reevaluation for one or more graded SAQ responses."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        user_id = session['user_id']
        response_ids = data.get('response_ids')
        reason = data.get('reason', '').strip()

        if not response_ids or not reason:
            return jsonify({'error': 'response_ids and reason are required'}), 400

        result = assessment_service.request_saq_reevaluation(user_id, response_ids, reason)
        return jsonify({
            'status': 'success',
            'data': result,
            'message': 'Reevaluation request submitted'
        })
    except Exception as e:
        print(f"Error requesting SAQ reevaluation: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to request reevaluation'}), 500


@assessment.route('/saq/result/<int:course_id>/<int:module_index>', methods=['GET'])
def get_saq_results(course_id, module_index):
    """Get SAQ submission and grading status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        user_id = session['user_id']
        
        responses = db_select(conn, """
            SELECT ssr.id, ssr.saq_id, ssr.answer_text, ssr.score, 
                   ssr.feedback, ssr.is_graded, saq.question_text, saq.max_score
            FROM student_saq_responses ssr
            JOIN short_answer_questions saq ON ssr.saq_id = saq.id
            WHERE ssr.user_id = %s AND ssr.course_id = %s AND ssr.module_index = %s
        """, (user_id, course_id, module_index))
        
        results = [
            {
                'id': r[0],
                'saq_id': r[1],
                'answer': r[2],
                'score': float(r[3]) if r[3] is not None else None,
                'feedback': r[4],
                'is_graded': bool(r[5]),
                'question': r[6],
                'max_score': r[7],
                'reevaluation': None
            }
            for r in responses
        ]

        if results:
            response_ids = [r['id'] for r in results]
            placeholders = ','.join(['%s'] * len(response_ids))
            reeval_rows = db_select(conn, f"""
                SELECT response_id, status, reason, requested_at
                FROM saq_reevaluation_requests
                WHERE user_id = %s AND response_id IN ({placeholders})
                ORDER BY requested_at DESC
            """, tuple([user_id] + response_ids))

            latest_requests = {}
            for rr in reeval_rows:
                response_id = rr[0]
                if response_id not in latest_requests:
                    latest_requests[response_id] = {
                        'status': rr[1],
                        'reason': rr[2],
                        'requested_at': rr[3].isoformat() if rr[3] else None
                    }

            for result in results:
                if result['id'] in latest_requests:
                    result['reevaluation'] = latest_requests[result['id']]

        module_summary = db_select_one(conn, """
            SELECT quiz_score_percentage, saq_score_percentage, module_score_percentage
            FROM module_assessment_results
            WHERE user_id = %s AND course_id = %s AND module_index = %s
        """, (user_id, course_id, module_index))

        if module_summary is None and results:
            # If module results are missing, calculate them now.
            module_score_val = assessment_service.calculate_module_assessment_score(
                user_id, course_id, module_index
            )
            module_summary = (None, None, module_score_val)

        summary = None
        if module_summary:
            summary = {
                'quiz_score_percentage': float(module_summary[0]) if module_summary[0] is not None else None,
                'saq_score_percentage': float(module_summary[1]) if module_summary[1] is not None else None,
                'module_score_percentage': float(module_summary[2]) if module_summary[2] is not None else None
            }

        conn.close()
        return jsonify({
            'status': 'success',
            'data': results,
            'module_summary': summary
        })
    except Exception as e:
        print(f"Error fetching SAQ results: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to load results'}), 500


# ==================== FINAL ASSESSMENT ROUTES ====================

@assessment.route('/final/<int:course_id>', methods=['GET'])
def get_final_assessment(course_id):
    """Get final assessment questions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        assessments = assessment_service.get_final_assessments(course_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'course_id': course_id,
                'questions': assessments,
                'total_questions': len(assessments)
            }
        })
    except Exception as e:
        print(f"Error fetching final assessment: {str(e)}")
        return jsonify({'error': 'Failed to load assessment'}), 500


@assessment.route('/final/submit', methods=['POST'])
def submit_final_assessment():
    """Submit final assessment response"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        result = assessment_service.submit_final_response(
            user_id,
            data['course_id'],
            data['final_assessment_id'],
            data['answer_text']
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        print(f"Error submitting final assessment: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to submit'}), 500


@assessment.route('/final/results/<int:course_id>', methods=['GET'])
def get_final_results(course_id):
    """Get final assessment submission and results"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        user_id = session['user_id']
        
        responses = db_select(conn, """
            SELECT sfr.id, sfr.final_assessment_id, sfr.answer_text, sfr.score,
                   sfr.feedback, sfr.is_graded, fa.question_text, fa.max_score
            FROM student_final_responses sfr
            JOIN final_assessments fa ON sfr.final_assessment_id = fa.id
            WHERE sfr.user_id = %s AND sfr.course_id = %s
        """, (user_id, course_id))
        
        conn.close()
        
        results = [
            {
                'id': r[0],
                'assessment_id': r[1],
                'answer': r[2],
                'score': float(r[3]) if r[3] else None,
                'feedback': r[4],
                'is_graded': bool(r[5]),
                'question': r[6],
                'max_score': r[7]
            }
            for r in responses
        ]
        
        return jsonify({
            'status': 'success',
            'data': results
        })
    except Exception as e:
        print(f"Error fetching final results: {str(e)}")
        return jsonify({'error': 'Failed to load results'}), 500


# ==================== LLM-BASED GRADING ENDPOINTS ====================

@assessment.route('/llm/grade-saq/<int:response_id>', methods=['POST'])
def llm_grade_saq(response_id):
    """Use LLM to suggest a grade for SAQ response"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        
        # Get response data
        response_data = db_select_one(conn, """
            SELECT ssr.id, ssr.answer_text, saq.question_text, saq.rubric, saq.max_score
            FROM student_saq_responses ssr
            JOIN short_answer_questions saq ON ssr.saq_id = saq.id
            WHERE ssr.id = %s
        """, (response_id,))
        
        conn.close()
        
        if not response_data:
            return jsonify({'error': 'Response not found'}), 404
        
        question_text = response_data[2]
        rubric = response_data[3]
        max_score = response_data[4]
        answer_text = response_data[1]
        
        if rubric:
            rubric = json.loads(rubric) if isinstance(rubric, str) else rubric
        
        # Get LLM grading suggestion
        grading_result = assessment_service.llm_grade_saq_response(
            question_text,
            rubric or {},
            answer_text,
            max_score
        )
        
        return jsonify({
            'status': 'success',
            'data': grading_result,
            'message': 'LLM grading suggestion provided'
        })
    except Exception as e:
        print(f"Error getting LLM grade: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to generate grade'}), 500


@assessment.route('/llm/grade-final/<int:response_id>', methods=['POST'])
def llm_grade_final(response_id):
    """Use LLM to suggest a grade for final assessment response"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        
        # Get response data
        response_data = db_select_one(conn, """
            SELECT sfr.id, sfr.answer_text, fa.question_text, fa.max_score
            FROM student_final_responses sfr
            JOIN final_assessments fa ON sfr.final_assessment_id = fa.id
            WHERE sfr.id = %s
        """, (response_id,))
        
        conn.close()
        
        if not response_data:
            return jsonify({'error': 'Response not found'}), 404
        
        question_text = response_data[2]
        max_score = response_data[3]
        answer_text = response_data[1]
        
        # Get LLM grading suggestion
        grading_result = assessment_service.llm_grade_final_response(
            question_text,
            answer_text,
            max_score=max_score
        )
        
        return jsonify({
            'status': 'success',
            'data': grading_result,
            'message': 'LLM grading suggestion provided'
        })
    except Exception as e:
        print(f"Error getting LLM grade: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to generate grade'}), 500


@assessment.route('/llm/apply-grade/<int:response_id>/<string:response_type>', methods=['POST'])
def apply_llm_grade(response_id, response_type):
    """Apply LLM-suggested grade to response and save it"""
    auth_resp = _require_instructor_or_admin()
    if auth_resp:
        return auth_resp

    course_id = _get_response_course_id(response_id, response_type)
    if not course_id:
        return jsonify({'error': 'Response not found'}), 404
    if not _user_has_access_to_course(course_id):
        return jsonify({'error': 'Forbidden'}), 403

    try:
        data = request.get_json()
        grader_id = session['user_id']
        score = data['score']
        feedback = data.get('feedback', '')
        
        if response_type == 'saq':
            result = assessment_service.grade_saq_response(
                response_id, score, feedback, grader_id
            )
        elif response_type == 'final':
            result = assessment_service.grade_final_response(
                response_id, score, feedback, grader_id
            )
        else:
            return jsonify({'error': 'Invalid response type'}), 400
        
        return jsonify({
            'status': 'success',
            'data': result,
            'message': f'{response_type.upper()} grade applied'
        })
    except Exception as e:
        print(f"Error applying grade: {str(e)}")
        return jsonify({'error': str(e)}), 500




@assessment.route('/grade/saq/<int:response_id>', methods=['POST'])
def grade_saq(response_id):
    """Grade a short answer question response"""
    auth_resp = _require_instructor_or_admin()
    if auth_resp:
        return auth_resp

    course_id = _get_response_course_id(response_id, 'saq')
    if not course_id:
        return jsonify({'error': 'Response not found'}), 404
    if not _user_has_access_to_course(course_id):
        return jsonify({'error': 'Forbidden'}), 403

    try:
        data = request.get_json()
        grader_id = session['user_id']
        
        result = assessment_service.grade_saq_response(
            response_id,
            data['score'],
            data.get('feedback', ''),
            grader_id
        )
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        print(f"Error grading SAQ: {str(e)}")
        return jsonify({'error': 'Failed to grade'}), 500


@assessment.route('/grade/final/<int:response_id>', methods=['POST'])
def grade_final(response_id):
    """Grade a final assessment response"""
    auth_resp = _require_instructor_or_admin()
    if auth_resp:
        return auth_resp

    course_id = _get_response_course_id(response_id, 'final')
    if not course_id:
        return jsonify({'error': 'Response not found'}), 404
    if not _user_has_access_to_course(course_id):
        return jsonify({'error': 'Forbidden'}), 403

    try:
        data = request.get_json()
        grader_id = session['user_id']
        
        result = assessment_service.grade_final_response(
            response_id,
            data['score'],
            data.get('feedback', ''),
            grader_id
        )
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        print(f"Error grading final: {str(e)}")
        return jsonify({'error': 'Failed to grade'}), 500


# ==================== RESULTS AND CERTIFICATE ROUTES ====================

@assessment.route('/completion/<int:course_id>', methods=['GET'])
def get_completion_status(course_id):
    """Get course completion and grading status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        status = assessment_service.get_course_completion_status(user_id, course_id)
        
        if status:
            return jsonify({
                'status': 'success',
                'data': status
            })
        else:
            return jsonify({
                'status': 'not_graded',
                'message': 'Course not yet graded'
            })
    except Exception as e:
        print(f"Error fetching completion status: {str(e)}")
        return jsonify({'error': 'Failed to load status'}), 500


@assessment.route('/certificate/<int:course_id>', methods=['GET'])
def get_certificate(course_id):
    """Get certificate if issued"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        cert = assessment_service.get_certificate(user_id, course_id)
        
        if cert:
            return jsonify({
                'status': 'issued',
                'data': cert
            })
        else:
            return jsonify({
                'status': 'not_issued',
                'message': 'Certificate not yet issued'
            })
    except Exception as e:
        print(f"Error fetching certificate: {str(e)}")
        return jsonify({'error': 'Failed to load certificate'}), 500


@assessment.route('/certificate/issue/<int:course_id>', methods=['POST'])
def issue_certificate(course_id):
    """Issue certificate to student (instructor only)"""
    auth_resp = _require_instructor_or_admin()
    if auth_resp:
        return auth_resp

    if not _user_has_access_to_course(course_id):
        return jsonify({'error': 'Forbidden'}), 403

    try:
        data = request.get_json()
        user_id = data['user_id']
        user_name = data.get('user_name', 'Student')
        course_title = data.get('course_title', 'Course')
        
        result = assessment_service.issue_certificate(
            user_id, course_id, user_name, course_title
        )
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        print(f"Error issuing certificate: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to issue certificate'}), 500


# ==================== MODULE ASSESSMENT CALCULATION ====================

@assessment.route('/calculate/module/<int:course_id>/<int:module_index>', methods=['POST'])
def calculate_module_score(course_id, module_index):
    """Calculate module assessment score (quiz + SAQ)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        score = assessment_service.calculate_module_assessment_score(
            user_id, course_id, module_index
        )
        
        return jsonify({
            'status': 'success',
            'data': {'module_score': round(score, 2)}
        })
    except Exception as e:
        print(f"Error calculating module score: {str(e)}")
        return jsonify({'error': 'Failed to calculate score'}), 500


@assessment.route('/calculate/final/<int:course_id>/<int:total_modules>', methods=['POST'])
def calculate_final_grade_route(course_id, total_modules):
    """Calculate final grade (40% modules + 60% final exam)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Calculate final grade
        grade_data = assessment_service.calculate_final_grade(
            user_id, course_id, total_modules
        )
        
        # If passed (score >= 70), issue certificate
        if grade_data['passed']:
            cert_result = assessment_service.issue_certificate(
                user_id, course_id, session.get('full_name', 'Student'), 
                'Course'  # TODO: Get actual course title
            )
            grade_data['certificate'] = cert_result
        
        return jsonify({
            'status': 'success',
            'data': grade_data
        })
    except Exception as e:
        print(f"Error calculating final grade: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to calculate grade'}), 500
