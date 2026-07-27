# Assessment System Examples

This file contains practical code examples for integrating assessments into your existing application.

## Example 1: Modify Course Save to Create Assessments

**Location**: `app/routes.py`

```python
# Add this import at the top
from app.services.assessment_service import assessment_service
import json

# Modify your existing save course function
@main.route('/save_course', methods=['POST'])
def save_course():
    """Save generated course with assessments"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    course_data = session.get('generated_course')
    
    if not course_data:
        return jsonify({'error': 'No course data found'}), 400
    
    conn = get_db_connection()
    
    try:
        # Calculate content hash to prevent duplicates
        content_str = json.dumps(course_data)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Check if course already exists
        existing = db_select_one(conn, """
            SELECT id FROM courses WHERE content_hash = %s
        """, (content_hash,))
        
        if existing:
            course_id = existing[0]
            flash(f"Course already exists (ID: {course_id})", "info")
        else:
            # Insert course
            course_id = db_insert(conn, """
                INSERT INTO courses 
                (title, description, content, content_hash, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                course_data.get('title'),
                course_data.get('description'),
                content_str,
                content_hash,
                user_id
            ))
            
            conn.commit()
            
            # NOW CREATE ASSESSMENTS
            _create_assessments_for_course(course_id, course_data)
            
            flash(f"Course saved successfully (ID: {course_id})", "success")
        
        return jsonify({
            'status': 'success',
            'course_id': course_id,
            'title': course_data.get('title')
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Error saving course: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def _create_assessments_for_course(course_id, course_data):
    """Helper function to create all assessments for a course"""
    try:
        modules = course_data.get('modules', [])
        
        for module_idx, module in enumerate(modules):
            # Create SAQ for this module
            saq_ids = assessment_service.create_saq_for_module(
                course_id, 
                module_idx, 
                module
            )
            print(f"Created {len(saq_ids)} SAQs for module {module_idx}")
            
            # Create quiz for each lesson in this module
            lessons = module.get('lessons', [])
            for lesson_idx, lesson in enumerate(lessons):
                quiz_ids = assessment_service.create_quiz_for_lesson(
                    course_id,
                    module_idx,
                    lesson_idx,
                    lesson
                )
                print(f"Created {len(quiz_ids)} quiz questions for lesson {lesson_idx}")
        
        # Create final assessment (for last module)
        final_ids = assessment_service.create_final_assessment(
            course_id, 
            course_data
        )
        print(f"Created {len(final_ids)} final assessment questions")
        
        print(f"✓ All assessments created for course {course_id}")
        
    except Exception as e:
        print(f"Error creating assessments: {str(e)}")
        traceback.print_exc()
```

## Example 2: Add Assessment Links to Course View

**Location**: `app/templates/student/view_course.html` (create or modify)

```html
{% extends "student/dashboard_base.html" %}

{% block content %}
<div class="container mt-4">
    <h2>{{ course.title }}</h2>
    
    <!-- Tabs for modules -->
    <ul class="nav nav-tabs" id="moduleTabs">
        {% for module in modules %}
        <li class="nav-item">
            <a class="nav-link {% if loop.first %}active{% endif %}" 
               href="#module{{ loop.index0 }}" data-bs-toggle="tab">
                Module {{ loop.index }}
            </a>
        </li>
        {% endfor %}
    </ul>
    
    <!-- Tab content -->
    <div class="tab-content" id="moduleTabContent">
        {% for module in modules %}
        <div class="tab-pane fade {% if loop.first %}show active{% endif %}" 
             id="module{{ loop.index0 }}">
            
            <h3>{{ module.title }}</h3>
            <p>{{ module.description }}</p>
            
            <!-- Lessons -->
            <div class="lessons-list">
                {% for lesson in module.lessons %}
                <div class="lesson-card card mb-3">
                    <div class="card-body">
                        <h5>{{ lesson.title }}</h5>
                        <p>{{ lesson.summary }}</p>
                        
                        <!-- Lesson content -->
                        <div class="lesson-content mb-3">
                            {{ lesson.content }}
                        </div>
                        
                        <!-- Assessment section -->
                        <div class="assessment-section bg-light p-3 rounded">
                            <h6>📚 Check Your Understanding</h6>
                            <p>Take the quiz to test what you've learned.</p>
                            <button class="btn btn-primary" 
                                    onclick="startQuiz({{ course.id }}, {{ loop.index0 }}, {{ loop.revindex0 }})">
                                📝 Take Lesson Quiz
                            </button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Module assessment -->
            <div class="module-completion card border-success mt-4">
                <div class="card-header bg-success text-white">
                    <h5>✅ Module {{ loop.index }} Complete!</h5>
                </div>
                <div class="card-body">
                    <p>You've completed all lessons in this module. 
                       Take the module assessment to test your overall understanding.</p>
                    <button class="btn btn-lg btn-success" 
                            onclick="startModuleAssessment({{ course.id }}, {{ loop.index0 }})">
                        ✍️ Complete Module Assessment
                    </button>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Final Assessment (after all modules) -->
    <div class="final-assessment card border-warning mt-5">
        <div class="card-header bg-warning">
            <h5>🎯 Final Assessment</h5>
        </div>
        <div class="card-body">
            <p>You've completed all modules! The final assessment is worth 60% of your grade.</p>
            <p>You need a score of 70% overall to receive your Certificate of Completion.</p>
            <button class="btn btn-lg btn-warning" 
                    onclick="startFinalAssessment({{ course.id }})">
                🎯 Take Final Assessment
            </button>
        </div>
    </div>
    
    <!-- View Results -->
    <div class="text-center mt-4 mb-4">
        <button class="btn btn-info btn-lg" 
                onclick="viewResults({{ course.id }})">
            📊 View My Results & Certificate
        </button>
    </div>
</div>

<script>
function startQuiz(courseId, moduleIdx, lessonIdx) {
    const url = `/templates/student/lesson_quiz.html?course=${courseId}&module=${moduleIdx}&lesson=${lessonIdx}`;
    window.location.href = url;
}

function startModuleAssessment(courseId, moduleIdx) {
    const url = `/templates/student/module_assessment.html?course=${courseId}&module=${moduleIdx}`;
    window.location.href = url;
}

function startFinalAssessment(courseId) {
    const url = `/templates/student/final_assessment.html?course=${courseId}`;
    window.location.href = url;
}

function viewResults(courseId) {
    const url = `/templates/student/course_completion.html?course=${courseId}`;
    window.location.href = url;
}
</script>
{% endblock %}
```

## Example 3: Update Student Dashboard to Show Completion Status

**Location**: `app/templates/student/student_dashboard.html` (modify existing)

```html
<!-- Add this to the course card section -->

{% for enrollment in enrollments %}
<div class="course-card card mb-3">
    <div class="card-header">
        <h5>{{ enrollment.course.title }}</h5>
    </div>
    <div class="card-body">
        <!-- Progress -->
        <div class="mb-3">
            <small>Progress</small>
            <div class="progress" style="height: 20px;">
                <div class="progress-bar" role="progressbar" 
                     style="width: {{ enrollment.progress }}%" 
                     aria-valuenow="{{ enrollment.progress }}" 
                     aria-valuemin="0" aria-valuemax="100">
                    {{ enrollment.progress }}%
                </div>
            </div>
        </div>
        
        <!-- Assessment Status Badge -->
        <div id="assessment-status-{{ enrollment.course_id }}" class="mb-3">
            <!-- Loaded by JavaScript -->
        </div>
        
        <!-- Action Buttons -->
        <div class="btn-group" role="group">
            <a href="/view_course/{{ enrollment.course_id }}" 
               class="btn btn-primary">
                📖 Continue Learning
            </a>
        </div>
    </div>
</div>
{% endfor %}

<script>
// Load assessment status for each enrolled course
document.addEventListener('DOMContentLoaded', function() {
    const enrollments = document.querySelectorAll('[id^="assessment-status-"]');
    enrollments.forEach(el => {
        const courseId = el.id.replace('assessment-status-', '');
        loadAssessmentStatus(courseId, el);
    });
});

function loadAssessmentStatus(courseId, element) {
    fetch(`/assessment/completion/${courseId}`)
        .then(r => r.json())
        .then(data => {
            let html = '';
            
            if (data.status === 'success') {
                const status = data.data;
                if (status.passed) {
                    html = `
                        <div class="alert alert-success mb-0">
                            <strong>✓ Completed</strong> - Grade: ${status.grade} (${status.score.toFixed(1)}%)
                            <a href="/templates/student/course_completion.html?course=${courseId}" 
                               class="btn btn-sm btn-info ms-2">
                                View Certificate
                            </a>
                        </div>
                    `;
                } else {
                    html = `
                        <div class="alert alert-warning mb-0">
                            <strong>⚠️ In Progress</strong> - Score: ${status.score.toFixed(1)}%
                        </div>
                    `;
                }
            } else if (data.status === 'not_graded') {
                html = `
                    <div class="alert alert-info mb-0">
                        <strong>⏳ Pending</strong> - Assessments submitted, waiting for grading
                    </div>
                `;
            }
            
            element.innerHTML = html;
        })
        .catch(err => {
            console.error('Error loading status:', err);
            element.innerHTML = '<div class="alert alert-secondary mb-0">Status unavailable</div>';
        });
}
</script>
```

## Example 4: Admin Grading Interface

**Location**: `app/routes.py` (add new route)

```python
@main.route('/admin/pending-grades')
def admin_pending_grades():
    """Admin page to grade pending responses"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    # TODO: Add admin role check
    
    conn = get_db_connection()
    
    try:
        # Get pending SAQs
        pending_saqs = db_select(conn, """
            SELECT ssr.id, ssr.user_id, u.full_name, saq.question_text, 
                   ssr.answer_text, c.title as course_title
            FROM student_saq_responses ssr
            JOIN users u ON ssr.user_id = u.id
            JOIN short_answer_questions saq ON ssr.saq_id = saq.id
            JOIN courses c ON ssr.course_id = c.id
            WHERE ssr.is_graded = 0
            ORDER BY ssr.submitted_at
        """)
        
        # Get pending final assessments
        pending_finals = db_select(conn, """
            SELECT sfr.id, sfr.user_id, u.full_name, fa.question_text,
                   sfr.answer_text, c.title as course_title
            FROM student_final_responses sfr
            JOIN users u ON sfr.user_id = u.id
            JOIN final_assessments fa ON sfr.final_assessment_id = fa.id
            JOIN courses c ON sfr.course_id = c.id
            WHERE sfr.is_graded = 0
            ORDER BY sfr.submitted_at
        """)
        
        return render_template('admin/grading_dashboard.html',
                             pending_saqs=pending_saqs,
                             pending_finals=pending_finals)
    finally:
        conn.close()


@main.route('/api/admin/grade-saq/<int:response_id>', methods=['POST'])
def api_grade_saq(response_id):
    """API endpoint to grade SAQ response"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    grader_id = session['user_id']
    
    try:
        result = assessment_service.grade_saq_response(
            response_id,
            data['score'],
            data.get('feedback', ''),
            grader_id
        )
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        print(f"Error grading: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

## Example 5: Mark Course as Complete When All Assessments Done

**Location**: `app/routes.py` (add new route)

```python
@main.route('/complete_course/<int:course_id>', methods=['POST'])
def complete_course(course_id):
    """Mark course as complete and calculate final grade"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    try:
        # Get course
        course = db_select_one(conn, """
            SELECT content FROM courses WHERE id = %s
        """, (course_id,))
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Calculate total modules
        course_data = json.loads(course[0])
        total_modules = len(course_data.get('modules', []))
        
        # Calculate final grade (40% modules + 60% final)
        grade_data = assessment_service.calculate_final_grade(
            user_id, course_id, total_modules
        )
        
        # Mark enrollment as completed
        db_update(conn, """
            UPDATE enrollments
            SET completed = 1, completed_at = NOW()
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))
        
        conn.commit()
        
        return jsonify({
            'status': 'success',
            'grade': grade_data['final_grade'],
            'score': grade_data['weighted_score'],
            'passed': grade_data['passed'],
            'certificate': grade_data.get('certificate')
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Error completing course: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
```

## Example 6: Configuration File for Assessment Settings

**Location**: `app/assessment_config.py` (create new)

```python
"""
Assessment Configuration
Centralized settings for the assessment system
"""

class AssessmentConfig:
    """Assessment system configuration"""
    
    # Grading Thresholds (percentages)
    QUIZ_PASSING_GRADE = 60
    MODULE_ASSESSMENT_PASSING_GRADE = 60
    FINAL_EXAM_PASSING_GRADE = 60
    OVERALL_CERTIFICATE_THRESHOLD = 70
    
    # Assessment Weights
    MODULE_ASSESSMENT_WEIGHT = 0.40  # 40%
    FINAL_ASSESSMENT_WEIGHT = 0.60   # 60%
    
    # Assessment Types
    QUIZ_ENABLED = True
    SAQ_ENABLED = True
    FINAL_ASSESSMENT_ENABLED = True
    
    # Auto-grading
    AUTO_GRADE_QUIZZES = True
    AUTO_CALCULATE_GRADES = True
    AUTO_ISSUE_CERTIFICATES = True
    
    # Retake Settings
    ALLOW_QUIZ_RETAKES = True
    ALLOW_SAQ_RESUBMISSION = False
    ALLOW_FINAL_RETAKES = False
    
    # Timing
    QUIZ_TIME_LIMIT = None  # Minutes (None = no limit)
    SAQ_TIME_LIMIT = None
    FINAL_EXAM_TIME_LIMIT = 180  # 3 hours
    
    # Letter Grades
    LETTER_GRADES = {
        'A': (90, 100),
        'B': (80, 89),
        'C': (70, 79),
        'D': (60, 69),
        'F': (0, 59)
    }

# Use in assessment_service.py
from app.assessment_config import AssessmentConfig

# Or in routes:
from app.assessment_config import AssessmentConfig
if AssessmentConfig.AUTO_ISSUE_CERTIFICATES:
    # Issue certificate automatically
```

## Usage in Your App

1. Copy assessment template files to `app/templates/student/`
2. Copy `assessment_service.py` to `app/services/`
3. Copy `routes_assessment.py` to `app/`
4. Import and register blueprint in your Flask app
5. Import assessment_service functions in your routes to create assessments
6. Add UI buttons/links to assessments in your templates
7. Test the complete flow

## Testing Checklist

- [ ] Create course and verify assessments are created in database
- [ ] Take lesson quiz and verify score is calculated
- [ ] Submit SAQ and verify submission recorded
- [ ] Grade SAQ response and verify score updated
- [ ] Submit final assessment and verify submission recorded
- [ ] Grade final assessment and verify grade calculated
- [ ] Verify certificate issued when score >= 70%
- [ ] View results page and verify all scores displayed
- [ ] Test with multiple users/courses
