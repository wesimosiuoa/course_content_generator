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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # TODO: Add instructor role check
    
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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # TODO: Add instructor/admin role check
    
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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # TODO: Add instructor/admin role check
    
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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # TODO: Add instructor/admin role check
    
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
