"""
Assessment Service - Handles quizzes, short answer questions, and final assessments
Implements grading logic, LLM-based question generation, and certificate generation
"""

from datetime import datetime
from decimal import Decimal
from app.db_management.db import get_db_connection
from app.db_management.sql import insert as db_insert
from app.db_management.sql import select as db_select
from app.db_management.sql import select_one as db_select_one
from app.db_management.sql import update as db_update
from app.services.llm_service import client  # Use Groq API client
import json
import hashlib
import uuid


# Passing thresholds
LESSON_QUIZ_THRESHOLD = 60  # 60% to pass
MODULE_ASSESSMENT_THRESHOLD = 60  # 60% to pass
FINAL_ASSESSMENT_THRESHOLD = 60  # 60% to pass
CERTIFICATE_THRESHOLD = 70  # 70% overall to get certificate

# Assessment weights
MODULE_ASSESSMENTS_WEIGHT = 0.40  # 40%
FINAL_ASSESSMENT_WEIGHT = 0.60  # 60%

# ==================== QUIZ METHODS ====================

def create_quiz_for_lesson(course_id, module_index, lesson_index, lesson_data):
    """
    Create quiz questions for a specific lesson
    Questions are generated from lesson content
    """
    try:
        conn = get_db_connection()

        # Get lesson title and summary from lesson_data
        lesson_title = lesson_data.get('title', f'Lesson {lesson_index + 1}')
        lesson_summary = lesson_data.get('summary', '')

        # Create 4-5 multiple choice questions from lesson content
        questions = _generate_quiz_questions(lesson_title, lesson_summary, lesson_data)

        question_ids = []
        for q_data in questions:
            # Insert question
            q_id = db_insert(conn, """
                INSERT INTO quiz_questions
                (course_id, module_index, lesson_index, question_text, question_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (course_id, module_index, lesson_index, q_data['question'], 'multiple_choice'))

            question_ids.append(q_id)

            # Insert answer options
            for idx, option in enumerate(q_data['options']):
                db_insert(conn, """
                    INSERT INTO quiz_answer_options
                    (question_id, option_text, is_correct, order_index)
                    VALUES (%s, %s, %s, %s)
                """, (q_id, option['text'], 1 if option['is_correct'] else 0, idx))

        conn.commit()
        return question_ids

    except Exception as e:
        print(f"Error creating quiz: {str(e)}")
        if conn:
            conn.rollback()
        raise

def _generate_quiz_questions(lesson_title, lesson_summary, lesson_data):
    """
    Generate quiz questions from lesson content using LLM
    Returns list of question dictionaries with options
    """
    try:
        # Get lesson content
        lesson_content = lesson_data.get('content', lesson_summary)

        prompt = f"""
        Generate 4-5 multiple choice quiz questions based on this lesson:

        Lesson Title: {lesson_title}
        Lesson Summary: {lesson_summary}

        For each question:
        - Create a clear, specific question
        - Provide 4 answer options
        - Mark the correct answer
        - Make wrong answers plausible but clearly incorrect

        Return ONLY valid JSON (no markdown, no explanation):
        {{
            "questions": [
                {{
                    "question": "Question text?",
                    "options": [
                        {{"text": "Option 1", "is_correct": true}},
                        {{"text": "Option 2", "is_correct": false}},
                        {{"text": "Option 3", "is_correct": false}},
                        {{"text": "Option 4", "is_correct": false}}
                    ]
                }}
            ]
        }}
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational assessment specialist creating clear, fair multiple choice quiz questions."
                },
                {"role": "user", "content": prompt}
            ],
                temperature=0.6
            )

            json_output = response.choices[0].message.content
            data = json.loads(json_output)
            return data.get('questions', [])

        except Exception as e:
            print(f"Error generating quiz questions with LLM: {str(e)}")
            # Fallback to basic template if LLM fails
            return [
                {
                    'question': f"What is the main topic covered in {lesson_title}?",
                    'options': [
                        {'text': lesson_summary[:50] if lesson_summary else 'The lesson content', 'is_correct': True},
                        {'text': 'A different topic', 'is_correct': False},
                        {'text': 'Unrelated information', 'is_correct': False},
                        {'text': 'Not covered in this lesson', 'is_correct': False},
                    ]
                }
            ]

def get_lesson_quiz(course_id, module_index, lesson_index):
    """Get all quiz questions for a lesson"""
    try:
        conn = get_db_connection()

        questions = db_select(conn, """
            SELECT id, question_text, question_type
            FROM quiz_questions
            WHERE course_id = %s AND module_index = %s AND lesson_index = %s
            ORDER BY id
        """, (course_id, module_index, lesson_index))

        quiz_data = []
        for q in questions:
            options = db_select(conn, """
                SELECT id, option_text, order_index
                FROM quiz_answer_options
                WHERE question_id = %s
                ORDER BY order_index
            """, (q[0],))

            quiz_data.append({
                'id': q[0],
                'question': q[1],
                'type': q[2],
                'options': [{'id': opt[0], 'text': opt[1], 'order': opt[2]} for opt in options]
            })

        return quiz_data

    except Exception as e:
        print(f"Error fetching quiz: {str(e)}")
        raise

def submit_quiz_response(user_id, course_id, module_index, lesson_index, responses):
    """
    Submit quiz responses for a lesson
    responses: list of {'question_id': int, 'selected_option_id': int}
    """
    try:
        conn = get_db_connection()

        total_questions = 0
        correct_answers = 0

        for response in responses:
            question_id = response['question_id']
            selected_option_id = response.get('selected_option_id')

            # Check if answer is correct
            correct_option = db_select_one(conn, """
                SELECT id FROM quiz_answer_options
                WHERE question_id = %s AND is_correct = 1
            """, (question_id,))

            is_correct = selected_option_id == correct_option[0] if correct_option else False

            # Record response
            db_insert(conn, """
                INSERT INTO student_quiz_responses
                (user_id, course_id, module_index, lesson_index,
                 question_id, selected_option_id, is_correct, score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, course_id, module_index, lesson_index,
                  question_id, selected_option_id, 1 if is_correct else 0,
                  1 if is_correct else 0))

            total_questions += 1
            if is_correct:
                correct_answers += 1

        # Calculate percentage
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        passed = 1 if score_percentage >= LESSON_QUIZ_THRESHOLD else 0

        # Insert or update lesson quiz result
        existing = db_select_one(conn, """
            SELECT id FROM lesson_quiz_results
                WHERE user_id = %s AND course_id = %s 
                AND module_index = %s AND lesson_index = %s
            """, (user_id, course_id, module_index, lesson_index))
            
            if existing:
                db_update(conn, """
                    UPDATE lesson_quiz_results
                    SET total_questions = %s, correct_answers = %s, 
                        score_percentage = %s, passed = %s, completed_at = NOW()
                    WHERE user_id = %s AND course_id = %s 
                    AND module_index = %s AND lesson_index = %s
                """, (total_questions, correct_answers, score_percentage, passed,
                      user_id, course_id, module_index, lesson_index))
            else:
                db_insert(conn, """
                    INSERT INTO lesson_quiz_results
                    (user_id, course_id, module_index, lesson_index, 
                     total_questions, correct_answers, score_percentage, passed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, course_id, module_index, lesson_index,
                      total_questions, correct_answers, score_percentage, passed))
            
            conn.commit()
            
            return {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'score_percentage': round(score_percentage, 2),
                'passed': bool(passed)
            }
            
        except Exception as e:
            print(f"Error submitting quiz: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
    # ==================== SHORT ANSWER QUESTION METHODS ====================
    
def create_saq_for_module(self, course_id, module_index, module_data):
        """Create short answer questions for a module"""
        try:
            conn = self.get_connection()
            
            module_title = module_data.get('title', f'Module {module_index + 1}')
            module_summary = module_data.get('summary', '')
            
            # Create 2-3 short answer questions
            questions = self._generate_saq_questions(module_title, module_summary, module_data)
            
            saq_ids = []
            for q_data in questions:
                saq_id = db_insert(conn, """
                    INSERT INTO short_answer_questions
                    (course_id, module_index, question_text, question_type, max_score, rubric)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (course_id, module_index, q_data['question'], 'short_answer', 10, 
                      json.dumps(q_data.get('rubric', {}))))
                
                saq_ids.append(saq_id)
            
            conn.commit()
            return saq_ids
            
        except Exception as e:
            print(f"Error creating SAQ: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
def _generate_saq_questions(self, module_title, module_summary, module_data):
        """Generate short answer questions from module content using LLM"""
        try:
            # Gather all lessons in the module for context
            lessons = module_data.get('lessons', [])
            lesson_summaries = '\n'.join([f"- {l.get('title')}: {l.get('summary')}" for l in lessons])
            
            prompt = f"""
            Generate 2-3 thoughtful short answer questions for this module assessment:
            
            Module Title: {module_title}
            Module Summary: {module_summary}
            
            Lessons in module:
            {lesson_summaries}
            
            Create questions that:
            - Test understanding of key module concepts
            - Require critical thinking and application
            - Cannot be answered with just memorization
            - Are appropriate for a 200-word answer range
            
            Include a grading rubric for each question (3-4 criteria).
            
            Return ONLY valid JSON (no markdown, no explanation):
            {{
                "questions": [
                    {{
                        "question": "Thoughtful question text?",
                        "rubric": {{
                            "criterion_1": "Description of what demonstrates mastery",
                            "criterion_2": "Description of what demonstrates mastery",
                            "criterion_3": "Description of what demonstrates mastery"
                        }}
                    }}
                ]
            }}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                messages=[
                    {{
                        "role": "system",
                        "content": "You are an expert educational assessment specialist creating insightful short answer assessment questions with clear rubrics."
                    }},
                    {{"role": "user", "content": prompt}}
                ],
                temperature=0.6
            )
            
            json_output = response.choices[0].message.content
            data = json.loads(json_output)
            return data.get('questions', [])
            
        except Exception as e:
            print(f"Error generating SAQ questions with LLM: {str(e)}")
            # Fallback to basic templates
            return [
                {
                    'question': f"Summarize the key concepts from {module_title}",
                    'rubric': {
                        'comprehensiveness': 'Covers all main points',
                        'clarity': 'Clear and well-organized',
                        'depth': 'Adequate depth of understanding'
                    }
                },
                {
                    'question': f"How would you apply what you learned in {module_title} to real-world scenarios?",
                    'rubric': {
                        'application': 'Demonstrates practical application',
                        'relevance': 'Examples are relevant',
                        'thinking': 'Shows critical thinking'
                    }
                }
            ]
    
def get_module_saqs(self, course_id, module_index):
        """Get all short answer questions for a module"""
        try:
            conn = self.get_connection()
            
            saqs = db_select(conn, """
                SELECT id, question_text, question_type, max_score, rubric
                FROM short_answer_questions
                WHERE course_id = %s AND module_index = %s
                ORDER BY id
            """, (course_id, module_index))
            
            return [
                {
                    'id': saq[0],
                    'question': saq[1],
                    'type': saq[2],
                    'max_score': saq[3],
                    'rubric': json.loads(saq[4]) if saq[4] else {}
                }
                for saq in saqs
            ]
            
        except Exception as e:
            print(f"Error fetching SAQs: {str(e)}")
            raise
    
def submit_saq_response(self, user_id, course_id, module_index, saq_id, answer_text):
        """Submit a short answer question response"""
        try:
            conn = self.get_connection()
            
            db_insert(conn, """
                INSERT INTO student_saq_responses
                (user_id, course_id, module_index, saq_id, answer_text)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, course_id, module_index, saq_id, answer_text))
            
            conn.commit()
            
            return {
                'status': 'submitted',
                'message': 'Answer submitted for grading'
            }
            
        except Exception as e:
            print(f"Error submitting SAQ: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
def grade_saq_response(self, response_id, score, feedback, graded_by_user_id):
        """Grade a short answer question response"""
        try:
            conn = self.get_connection()
            
            db_update(conn, """
                UPDATE student_saq_responses
                SET score = %s, feedback = %s, is_graded = 1, 
                    graded_by_user_id = %s, graded_at = NOW()
                WHERE id = %s
            """, (score, feedback, graded_by_user_id, response_id))
            
            conn.commit()
            return {'status': 'graded', 'message': 'Response graded successfully'}
            
        except Exception as e:
            print(f"Error grading SAQ: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
    # ==================== FINAL ASSESSMENT METHODS ====================
    
def create_final_assessment(self, course_id, course_data):
        """Create final assessment questions for the course"""
        try:
            conn = self.get_connection()
            
            # Create 3-5 essay questions for final assessment
            questions = self._generate_final_questions(course_data)
            
            final_ids = []
            for idx, q_data in enumerate(questions):
                final_id = db_insert(conn, """
                    INSERT INTO final_assessments
                    (course_id, question_id, question_text, max_score)
                    VALUES (%s, %s, %s, %s)
                """, (course_id, idx, q_data['question'], 20))
                
                final_ids.append(final_id)
            
            conn.commit()
            return final_ids
            
        except Exception as e:
            print(f"Error creating final assessment: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
def _generate_final_questions(self, course_data):
        """Generate final assessment questions using LLM"""
        try:
            course_title = course_data.get('title', 'Course')
            course_overview = course_data.get('overview', '')
            learning_outcomes = course_data.get('learning_outcomes', [])
            
            # Get module titles for context
            modules = course_data.get('modules', [])
            module_titles = '\n'.join([f"- {m.get('title')}" for m in modules[:5]])
            
            prompt = f"""
            Generate 3-4 comprehensive essay questions for the final assessment of this course.
            
            Course: {course_title}
            Overview: {course_overview}
            
            Module Titles:
            {module_titles}
            
            Learning Outcomes students should demonstrate:
            {json.dumps(learning_outcomes[:5], indent=2)}
            
            Create questions that:
            - Test synthesis of multiple module concepts
            - Require deep understanding and critical analysis
            - Allow students to demonstrate mastery of learning outcomes
            - Are appropriate for a 500-1000 word essay response
            - Vary in scope (some narrow, some broad)
            
            Each question should have:
            - Clear prompt
            - Guidance on what constitutes a complete answer
            - Key concepts that should be addressed
            
            Return ONLY valid JSON (no markdown, no explanation):
            {{
                "questions": [
                    {{
                        "question": "Essay question text?",
                        "guidance": "What a complete answer should include",
                        "key_concepts": ["concept 1", "concept 2", "concept 3"]
                    }}
                ]
            }}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                messages=[
                    {{
                        "role": "system",
                        "content": "You are an expert educational assessment specialist creating comprehensive final exam essay questions."
                    }},
                    {{"role": "user", "content": prompt}}
                ],
                temperature=0.6
            )
            
            json_output = response.choices[0].message.content
            data = json.loads(json_output)
            return data.get('questions', [])
            
        except Exception as e:
            print(f"Error generating final questions with LLM: {str(e)}")
            # Fallback questions
            return [
                {
                    'question': f"Provide a comprehensive overview of the key concepts covered in {course_data.get('title', 'this course')}"
                },
                {
                    'question': f"How have you applied the knowledge from {course_data.get('title', 'this course')} to solve real-world problems?"
                },
                {
                    'question': f"Reflect on your learning journey and identify areas for future growth in {course_data.get('title', 'this course')}"
                }
            ]
    
def get_final_assessments(self, course_id):
        """Get all final assessment questions for a course"""
        try:
            conn = self.get_connection()
            
            assessments = db_select(conn, """
                SELECT id, question_text, max_score
                FROM final_assessments
                WHERE course_id = %s
                ORDER BY question_id
            """, (course_id,))
            
            return [
                {
                    'id': a[0],
                    'question': a[1],
                    'max_score': a[2]
                }
                for a in assessments
            ]
            
        except Exception as e:
            print(f"Error fetching final assessments: {str(e)}")
            raise
    
def submit_final_response(self, user_id, course_id, final_assessment_id, answer_text):
        """Submit final assessment response"""
        try:
            conn = self.get_connection()
            
            db_insert(conn, """
                INSERT INTO student_final_responses
                (user_id, course_id, final_assessment_id, answer_text)
                VALUES (%s, %s, %s, %s)
            """, (user_id, course_id, final_assessment_id, answer_text))
            
            conn.commit()
            return {'status': 'submitted', 'message': 'Final assessment submitted'}
            
        except Exception as e:
            print(f"Error submitting final assessment: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
def grade_final_response(self, response_id, score, feedback, graded_by_user_id):
        """Grade final assessment response"""
        try:
            conn = self.get_connection()
            
            db_update(conn, """
                UPDATE student_final_responses
                SET score = %s, feedback = %s, is_graded = 1,
                    graded_by_user_id = %s, graded_at = NOW()
                WHERE id = %s
            """, (score, feedback, graded_by_user_id, response_id))
            
            conn.commit()
            return {'status': 'graded', 'message': 'Final assessment graded'}
            
        except Exception as e:
            print(f"Error grading final assessment: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
    # ==================== GRADE CALCULATION METHODS ====================
    
def calculate_module_assessment_score(self, user_id, course_id, module_index):
        """Calculate overall score for a module (quiz + SAQ average)"""
        try:
            conn = self.get_connection()
            
            # Get quiz score
            quiz_result = db_select_one(conn, """
                SELECT score_percentage FROM lesson_quiz_results
                WHERE user_id = %s AND course_id = %s AND module_index = %s
                ORDER BY completed_at DESC LIMIT 1
            """, (user_id, course_id, module_index))
            
            quiz_score = quiz_result[0] if quiz_result else 0
            
            # Get average SAQ score
            saq_results = db_select(conn, """
                SELECT score FROM student_saq_responses
                WHERE user_id = %s AND course_id = %s 
                AND module_index = %s AND is_graded = 1
            """, (user_id, course_id, module_index))
            
            if saq_results:
                saq_scores = [Decimal(str(r[0])) for r in saq_results if r[0]]
                saq_avg = float(sum(saq_scores) / len(saq_scores)) if saq_scores else 0
            else:
                saq_avg = 0
            
            # Combined module score (quiz and SAQ average)
            module_score = (quiz_score + saq_avg) / 2 if saq_results else quiz_score
            
            # Update module assessment result
            existing = db_select_one(conn, """
                SELECT id FROM module_assessment_results
                WHERE user_id = %s AND course_id = %s AND module_index = %s
            """, (user_id, course_id, module_index))
            
            if existing:
                db_update(conn, """
                    UPDATE module_assessment_results
                    SET quiz_score_percentage = %s, saq_score_percentage = %s,
                        module_score_percentage = %s, completed = 1, completed_at = NOW()
                    WHERE user_id = %s AND course_id = %s AND module_index = %s
                """, (quiz_score, saq_avg, module_score, user_id, course_id, module_index))
            else:
                db_insert(conn, """
                    INSERT INTO module_assessment_results
                    (user_id, course_id, module_index, quiz_score_percentage, 
                     saq_score_percentage, module_score_percentage, completed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, course_id, module_index, quiz_score, saq_avg, module_score, 1))
            
            conn.commit()
            return module_score
            
        except Exception as e:
            print(f"Error calculating module score: {str(e)}")
            raise
    
def calculate_final_grade(self, user_id, course_id, total_modules):
        """
        Calculate final grade for course
        40% from module assessments, 60% from final assessment
        """
        try:
            conn = self.get_connection()
            
            # Get average of all module assessment scores
            module_scores = db_select(conn, """
                SELECT module_score_percentage FROM module_assessment_results
                WHERE user_id = %s AND course_id = %s
                ORDER BY module_index
            """, (user_id, course_id))
            
            if module_scores:
                module_avg = sum(float(m[0]) for m in module_scores) / len(module_scores)
            else:
                module_avg = 0
            
            # Get final assessment average score
            final_scores = db_select(conn, """
                SELECT score FROM student_final_responses
                WHERE user_id = %s AND course_id = %s AND is_graded = 1
            """, (user_id, course_id))
            
            if final_scores:
                # Convert scores out of 100
                final_avg = sum(float(f[0]) * 5 for f in final_scores if f[0]) / len(final_scores) if final_scores else 0
            else:
                final_avg = 0
            
            # Calculate weighted score (40% modules + 60% final)
            weighted_score = (module_avg * self.MODULE_ASSESSMENTS_WEIGHT) + \
                           (final_avg * self.FINAL_ASSESSMENT_WEIGHT)
            
            passed = 1 if weighted_score >= self.CERTIFICATE_THRESHOLD else 0
            
            # Determine letter grade
            if weighted_score >= 90:
                grade = 'A'
            elif weighted_score >= 80:
                grade = 'B'
            elif weighted_score >= 70:
                grade = 'C'
            elif weighted_score >= 60:
                grade = 'D'
            else:
                grade = 'F'
            
            # Insert or update final grade
            existing = db_select_one(conn, """
                SELECT id FROM course_completion_grades
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))
            
            if existing:
                db_update(conn, """
                    UPDATE course_completion_grades
                    SET module_assessments_avg = %s, final_assessment_score = %s,
                        weighted_score = %s, final_grade = %s, passed = %s
                    WHERE user_id = %s AND course_id = %s
                """, (module_avg, final_avg, weighted_score, grade, passed, user_id, course_id))
            else:
                db_insert(conn, """
                    INSERT INTO course_completion_grades
                    (user_id, course_id, module_assessments_avg, final_assessment_score,
                     weighted_score, final_grade, passed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, course_id, module_avg, final_avg, weighted_score, grade, passed))
            
            conn.commit()
            
            return {
                'module_average': round(module_avg, 2),
                'final_assessment_score': round(final_avg, 2),
                'weighted_score': round(weighted_score, 2),
                'final_grade': grade,
                'passed': bool(passed)
            }
            
        except Exception as e:
            print(f"Error calculating final grade: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
    # ==================== LLM-BASED GRADING METHODS ====================
    
def llm_grade_saq_response(self, question_text, rubric, answer_text, max_score=10):
        """
        Use LLM to grade a short answer question response
        Returns score and detailed feedback
        """
        try:
            rubric_text = json.dumps(rubric, indent=2) if isinstance(rubric, dict) else str(rubric)
            
            prompt = f"""
            Grade this short answer question response based on the provided rubric.
            
            Question: {question_text}
            
            Grading Rubric:
            {rubric_text}
            
            Student Answer:
            {answer_text}
            
            Provide:
            1. A score out of {max_score} (numeric only)
            2. Detailed feedback addressing each rubric criterion
            3. What the student did well
            4. Areas for improvement
            
            Return ONLY valid JSON (no markdown, no explanation):
            {{
                "score": 8.5,
                "score_out_of": {max_score},
                "feedback": "Detailed feedback text",
                "strengths": ["strength 1", "strength 2"],
                "improvements": ["area 1", "area 2"],
                "confidence": 0.92
            }}
            
            Confidence should be 0.0-1.0 indicating how confident the AI is in this grade.
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                messages=[
                    {{
                        "role": "system",
                        "content": "You are an expert educational evaluator providing fair, constructive grading and feedback based on rubrics."
                    }},
                    {{"role": "user", "content": prompt}}
                ],
                temperature=0.4  # Lower temperature for more consistent grading
            )
            
            json_output = response.choices[0].message.content
            grading_result = json.loads(json_output)
            return grading_result
            
        except Exception as e:
            print(f"Error grading SAQ with LLM: {str(e)}")
            return {
                'score': 0,
                'feedback': 'Unable to grade automatically. Please review manually.',
                'confidence': 0
            }
    
def llm_grade_final_response(self, question_text, answer_text, key_concepts=None, max_score=20):
        """
        Use LLM to grade a final assessment essay response
        """
        try:
            concepts_text = ""
            if key_concepts:
                concepts_text = f"\nKey concepts that should be addressed:\n" + \
                                "\n".join([f"- {c}" for c in key_concepts])
            
            prompt = f"""
            Grade this final assessment essay response.
            
            Essay Question: {question_text}
            {concepts_text}
            
            Student Essay:
            {answer_text}
            
            Evaluate based on:
            - Comprehensiveness (covers main topics)
            - Critical Thinking (analysis and synthesis)
            - Clarity (well-organized and clear)
            - Evidence (supports claims with examples)
            - Depth (demonstrates genuine understanding)
            
            Provide:
            1. Score out of {max_score}
            2. Assessment of each criterion (1-5 scale)
            3. What demonstrates mastery or not
            4. Specific feedback for improvement
            
            Return ONLY valid JSON (no markdown, no explanation):
            {{
                "score": 18,
                "score_out_of": {max_score},
                "criteria": {{
                    "comprehensiveness": {{"rating": 5, "comment": "..."}},
                    "critical_thinking": {{"rating": 4, "comment": "..."}},
                    "clarity": {{"rating": 5, "comment": "..."}},
                    "evidence": {{"rating": 4, "comment": "..."}},
                    "depth": {{"rating": 4, "comment": "..."}}
                }},
                "overall_feedback": "...",
                "strengths": ["strength 1", "strength 2"],
                "improvements": ["improvement 1", "improvement 2"],
                "confidence": 0.88
            }}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                messages=[
                    {{
                        "role": "system",
                        "content": "You are an expert college-level essay grader providing thorough, fair evaluation and constructive feedback."
                    }},
                    {{"role": "user", "content": prompt}}
                ],
                temperature=0.4
            )
            
            json_output = response.choices[0].message.content
            grading_result = json.loads(json_output)
            return grading_result
            
        except Exception as e:
            print(f"Error grading final response with LLM: {str(e)}")
            return {
                'score': 0,
                'feedback': 'Unable to grade automatically. Please review manually.',
                'confidence': 0
            }
    

    
def issue_certificate(self, user_id, course_id, user_name, course_title):
        """Issue certificate if student passed the course"""
        try:
            conn = self.get_connection()
            
            # Check if student passed
            grade_info = db_select_one(conn, """
                SELECT passed, weighted_score FROM course_completion_grades
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))
            
            if not grade_info or not grade_info[0]:
                return {'status': 'failed', 'message': 'Student has not achieved passing grade'}
            
            # Generate unique certificate code
            cert_code = self._generate_certificate_code(user_id, course_id)
            
            # Insert certificate
            db_insert(conn, """
                INSERT INTO certificates
                (user_id, course_id, certificate_code)
                VALUES (%s, %s, %s)
            """, (user_id, course_id, cert_code))
            
            # Mark certificate as issued in grades table
            db_update(conn, """
                UPDATE course_completion_grades
                SET certificate_issued = 1, certificate_issued_date = NOW()
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))
            
            conn.commit()
            
            return {
                'status': 'issued',
                'certificate_code': cert_code,
                'issues_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error issuing certificate: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
def _generate_certificate_code(self, user_id, course_id):
        """Generate unique certificate verification code"""
        data = f"{user_id}_{course_id}_{datetime.now().isoformat()}"
        hash_code = hashlib.sha256(data.encode()).hexdigest()[:12].upper()
        return hash_code
    
def get_certificate(self, user_id, course_id):
        """Get certificate info if issued"""
        try:
            conn = self.get_connection()
            
            cert = db_select_one(conn, """
                SELECT id, certificate_code, issue_date
                FROM certificates
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))
            
            if cert:
                return {
                    'id': cert[0],
                    'certificate_code': cert[1],
                    'issue_date': cert[2].isoformat() if cert[2] else None
                }
            return None
            
        except Exception as e:
            print(f"Error fetching certificate: {str(e)}")
            raise
    
def get_course_completion_status(self, user_id, course_id):
        """Get overall completion and grading status"""
        try:
            conn = self.get_connection()
            
            status = db_select_one(conn, """
                SELECT weighted_score, final_grade, passed, certificate_issued
                FROM course_completion_grades
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))
            
            if status:
                return {
                    'score': status[0],
                    'grade': status[1],
                    'passed': bool(status[2]),
                    'certificate_issued': bool(status[3])
                }
            return None
            
        except Exception as e:
            print(f"Error fetching completion status: {str(e)}")
            raise


# Create singleton instance
assessment_service = AssessmentService()
