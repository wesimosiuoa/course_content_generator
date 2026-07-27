# Assessment System Integration Guide

## Quick Start

This guide shows how to integrate the assessment system into your existing Course Generation application.

## Step 1: Setup Database

1. Import the assessment tables:
```bash
mysql -u root -p phosholi < assessment_tables.sql
```

2. Verify tables created:
```sql
SHOW TABLES LIKE '%assessment%';
SHOW TABLES LIKE '%quiz%';
SHOW TABLES LIKE '%certificate%';
```

## Step 2: Register Assessment Blueprint

Open `app/__init__.py` or your Flask app initialization file and add:

```python
from flask import Flask
from app.routes import main

def create_app():
    app = Flask(__name__)
    
    # Register main blueprint
    app.register_blueprint(main)
    
    # Register assessment blueprint
    from app.routes_assessment import assessment
    app.register_blueprint(assessment)
    
    return app
```

Or in `run.py`:
```python
from flask import Flask
from app.routes import main
from app.routes_assessment import assessment

app = Flask(__name__)
app.secret_key = 'your-secret-key'

app.register_blueprint(main)
app.register_blueprint(assessment)

if __name__ == '__main__':
    app.run(debug=True)
```

## Step 3: Create Assessment When Course is Saved

When saving a generated course, create assessments:

```python
# In routes.py, after saving course to database
from app.services.assessment_service import assessment_service

@main.route('/save_course', methods=['POST'])
def save_course():
    # ... existing course save code ...
    
    course_id = db_insert(conn, """
        INSERT INTO courses (title, description, content, ...)
        VALUES (%s, %s, %s, ...)
    """, (...))
    
    # Get course content
    course_data = session.get('generated_course')
    modules = course_data.get('modules', [])
    
    # Create assessments for each module and lesson
    for module_idx, module in enumerate(modules):
        # Create SAQ for module
        assessment_service.create_saq_for_module(course_id, module_idx, module)
        
        # Create quizzes for each lesson
        for lesson_idx, lesson in enumerate(module.get('lessons', [])):
            assessment_service.create_quiz_for_lesson(
                course_id, module_idx, lesson_idx, lesson
            )
    
    # Create final assessment
    assessment_service.create_final_assessment(course_id, course_data)
    
    return jsonify({'status': 'success', 'course_id': course_id})
```

## Step 4: Add Assessment Links to Course View

In `student/view_course.html`:

```html
<!-- After lesson content -->
<div class="lesson-actions mt-4">
    <a href="/templates/student/lesson_quiz.html?course={{ course.id }}&module={{ module_idx }}&lesson={{ lesson_idx }}" 
       class="btn btn-primary">
        📝 Take Lesson Quiz
    </a>
</div>

<!-- At end of module -->
<div class="module-completion">
    <h4>Module {{ module_idx + 1 }} Complete!</h4>
    <p>Complete the module assessment to test your knowledge.</p>
    <a href="/templates/student/module_assessment.html?course={{ course.id }}&module={{ module_idx }}" 
       class="btn btn-secondary btn-lg">
        ✍️ Complete Module Assessment
    </a>
</div>

<!-- For last module -->
{% if module_idx == total_modules - 1 %}
<div class="final-assessment">
    <h4>Ready for Final Assessment?</h4>
    <p>The final assessment is worth 60% of your grade. You need 70% to earn your certificate.</p>
    <a href="/templates/student/final_assessment.html?course={{ course.id }}" 
       class="btn btn-warning btn-lg">
        🎯 Take Final Assessment
    </a>
</div>
{% endif %}
```

## Step 5: Add Completion Status to Dashboard

Update `student_dashboard.html`:

```html
{% for enrollment in courses %}
<div class="course-card">
    <h5>{{ enrollment.course.title }}</h5>
    
    <!-- Progress bar -->
    <div class="progress">
        <div class="progress-bar" role="progressbar" 
             style="width: {{ enrollment.progress }}%">
            {{ enrollment.progress }}%
        </div>
    </div>
    
    <!-- Assessment status -->
    <div class="assessment-status">
        {% if enrollment.completed %}
            <div class="alert alert-success">
                <strong>Course Complete!</strong>
                <a href="/templates/student/course_completion.html?course={{ enrollment.course_id }}" 
                   class="btn btn-sm btn-info">
                    📊 View Results
                </a>
            </div>
        {% else %}
            <div class="alert alert-info">
                <a href="/templates/student/view_course.html?course={{ enrollment.course_id }}" 
                   class="btn btn-primary">
                    Continue Learning
                </a>
            </div>
        {% endif %}
    </div>
</div>
{% endfor %}
```

## Step 6: Update Course Completion Logic

In `routes.py`, when marking course as complete:

```python
@main.route('/complete_course/<int:course_id>', methods=['POST'])
def complete_course(course_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    try:
        # Get number of modules
        course = db_select_one(conn, """
            SELECT content FROM courses WHERE id = %s
        """, (course_id,))
        
        if course:
            course_data = json.loads(course[0])
            total_modules = len(course_data.get('modules', []))
            
            # Calculate final grade
            grade_result = assessment_service.calculate_final_grade(
                user_id, course_id, total_modules
            )
            
            # Mark enrollment as complete
            db_update(conn, """
                UPDATE enrollments 
                SET completed = 1, completed_at = NOW()
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'grade': grade_result['final_grade'],
                'score': grade_result['weighted_score'],
                'passed': grade_result['passed']
            })
        else:
            return jsonify({'error': 'Course not found'}), 404
            
    finally:
        conn.close()
```

## Step 7: (Optional) Create Admin Interface for Grading

Create `app/templates/admin/grading_dashboard.html`:

```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h2>Grading Dashboard</h2>
    
    <div class="row">
        <!-- Pending SAQs -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">Pending Short Answer Questions</div>
                <div class="card-body">
                    <div id="pending-saqs">Loading...</div>
                </div>
            </div>
        </div>
        
        <!-- Pending Final Assessments -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">Pending Final Assessments</div>
                <div class="card-body">
                    <div id="pending-finals">Loading...</div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // Load pending responses
    fetch('/api/admin/pending-grades')
        .then(r => r.json())
        .then(data => {
            // Display pending SAQs and finals
        });
</script>
{% endblock %}
```

## Step 8: Enable Assessments in View Course Page

Update the lesson viewer to include quiz links:

```html
<!-- In student/view_course.html or similar -->

<div class="lesson-content">
    <h4>{{ lesson.title }}</h4>
    <p>{{ lesson.content }}</p>
</div>

<!-- Assessment section at bottom of lesson -->
<div class="lesson-assessment mt-4 p-3 bg-light rounded">
    <h5>📚 Check Your Understanding</h5>
    <p>Take the quiz below to test what you've learned in this lesson.</p>
    <button class="btn btn-primary" onclick="startQuiz({{ course_id }}, {{ module_idx }}, {{ lesson_idx }})">
        Start Quiz
    </button>
</div>

<script>
function startQuiz(courseId, moduleIdx, lessonIdx) {
    window.location.href = `/templates/student/lesson_quiz.html?course=${courseId}&module=${moduleIdx}&lesson=${lessonIdx}`;
}
</script>
```

## File Structure

After integration, your assessment files should be organized as:

```
course_content_generator/
├── app/
│   ├── services/
│   │   └── assessment_service.py          # NEW
│   ├── templates/
│   │   └── student/
│   │       ├── lesson_quiz.html            # NEW
│   │       ├── module_assessment.html      # NEW
│   │       ├── final_assessment.html       # NEW
│   │       └── course_completion.html      # NEW
│   ├── routes_assessment.py                # NEW
│   └── routes.py                           # MODIFIED
├── assessment_tables.sql                   # NEW
└── ASSESSMENT_SYSTEM.md                    # NEW
```

## Testing the Assessment System

### 1. Test Quiz Flow
```bash
curl -X GET "http://localhost:5000/assessment/quiz/1/0/0" \
  -H "Cookie: session=YOUR_SESSION_ID"
```

### 2. Test Quiz Submission
```bash
curl -X POST "http://localhost:5000/assessment/quiz/submit" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_ID" \
  -d '{
    "course_id": 1,
    "module_index": 0,
    "lesson_index": 0,
    "responses": [
      {"question_id": 1, "selected_option_id": 1},
      {"question_id": 2, "selected_option_id": 4}
    ]
  }'
```

### 3. Test Final Grade Calculation
```bash
curl -X POST "http://localhost:5000/assessment/calculate/final/1/4" \
  -H "Cookie: session=YOUR_SESSION_ID"
```

## Configuration

To customize assessment settings, edit `assessment_service.py`:

```python
class AssessmentService:
    # Passing thresholds
    LESSON_QUIZ_THRESHOLD = 60        # Change to require higher quiz scores
    MODULE_ASSESSMENT_THRESHOLD = 60
    FINAL_ASSESSMENT_THRESHOLD = 60
    CERTIFICATE_THRESHOLD = 70        # Change to require different overall score
    
    # Assessment weights
    MODULE_ASSESSMENTS_WEIGHT = 0.40
    FINAL_ASSESSMENT_WEIGHT = 0.60
```

## Common Tasks

### Add More Quiz Questions
```python
# In assessment_service.py
def _generate_quiz_questions(self, lesson_title, lesson_summary, lesson_data):
    questions = [
        # Add more question templates here
    ]
    return questions
```

### Change Certificate Threshold
Change `CERTIFICATE_THRESHOLD` in AssessmentService class (default 70%).

### Enable/Disable Assessment Type
Comment out the assessment creation calls in your course save function.

## Support & Troubleshooting

See [ASSESSMENT_SYSTEM.md](ASSESSMENT_SYSTEM.md) for detailed documentation and troubleshooting.

## Next Steps

1. ✅ Import `assessment_tables.sql` into database
2. ✅ Update `app/__init__.py` to register blueprint
3. ✅ Add assessment creation when saving courses
4. ✅ Add UI buttons to course view pages
5. ✅ Test quiz submission flow
6. ✅ Test grade calculation
7. ✅ (Optional) Create grading dashboard for instructors
8. ✅ Deploy to production
