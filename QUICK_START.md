# Assessment System - Quick Start Guide

Get the assessment system up and running in 5 minutes!

## Prerequisites
- Course Generation application already running
- MySQL database access
- The application files already created

## 🚀 5-Minute Setup

### Step 1: Import Database Tables (1 min)

```bash
# Navigate to project directory
cd c:\xampp\htdocs\course-gen

# Import the assessment tables
mysql -u root -p phosholi < assessment_tables.sql
```

**Verify import:**
```sql
mysql -u root -p phosholi

USE phosholi;
SHOW TABLES LIKE '%quiz%';
SHOW TABLES LIKE '%assessment%';
SHOW TABLES LIKE '%certificate%';

# You should see 11 new tables
```

### Step 2: Update Flask App (1 min)

Find your Flask app initialization file (likely `run.py` or `app/__init__.py`) and add:

**In `run.py` or similar:**
```python
# Add this import
from app.routes_assessment import assessment

# Add this after app creation
app.register_blueprint(assessment)
```

### Step 3: Restart Application (1 min)

```bash
# Kill existing Flask process
# Start your Flask app again
python run.py
```

### Step 4: Test Assessment Routes (1 min)

Open a browser and test:
```
http://localhost:5000/assessment/quiz/1/0/0
http://localhost:5000/assessment/saq/1/0
http://localhost:5000/assessment/final/1
```

You should get JSON responses (or errors if course doesn't exist).

### Step 5: Create Course with Assessments (1 min)

Modify your course save function in `routes.py`:

```python
@main.route('/save_course', methods=['POST'])
def save_course():
    # ... existing code to create course ...
    
    course_id = db_insert(conn, """
        INSERT INTO courses (title, description, content, ...)
        VALUES (%s, %s, %s, ...)
    """, (...))
    
    # ADD THESE LINES:
    from app.services.assessment_service import assessment_service
    course_data = session.get('generated_course')
    modules = course_data.get('modules', [])
    
    for module_idx, module in enumerate(modules):
        assessment_service.create_saq_for_module(course_id, module_idx, module)
        for lesson_idx, lesson in enumerate(module.get('lessons', [])):
            assessment_service.create_quiz_for_lesson(course_id, module_idx, lesson_idx, lesson)
    
    assessment_service.create_final_assessment(course_id, course_data)
    
    return jsonify({'status': 'success', 'course_id': course_id})
```

## ✅ Verification Checklist

- [ ] Database tables imported successfully
- [ ] Flask app starts without errors
- [ ] Assessment API routes accessible
- [ ] Course created with assessments
- [ ] Quiz questions visible in database

## 🎯 Test the Full Flow (10 minutes)

### 1. Take a Quiz
```
Navigate to: /templates/student/lesson_quiz.html?course=1&module=0&lesson=0
Select an answer and submit
Verify you see the score
```

### 2. Submit Module Assessment
```
Navigate to: /templates/student/module_assessment.html?course=1&module=0
Type answers and submit
Verify submission message
```

### 3. Submit Final Assessment
```
Navigate to: /templates/student/final_assessment.html?course=1
Type answers and submit
Verify submission message
```

### 4. Check Completion Status
```
Navigate to: /templates/student/course_completion.html?course=1
You should see pending grading status
```

## 📊 Grading (Manual Step)

Grade student responses:

```bash
# Using curl to grade SAQ
curl -X POST "http://localhost:5000/assessment/grade/saq/1" \
  -H "Content-Type: application/json" \
  -d '{"score": 8.5, "feedback": "Good work!"}'

# Using curl to grade final assessment
curl -X POST "http://localhost:5000/assessment/grade/final/1" \
  -H "Content-Type: application/json" \
  -d '{"score": 18, "feedback": "Excellent!"}'
```

## 🔗 Essential Links

### Documentation
- Overall System: [ASSESSMENT_SYSTEM.md](ASSESSMENT_SYSTEM.md)
- Integration Steps: [ASSESSMENT_INTEGRATION.md](ASSESSMENT_INTEGRATION.md)
- Code Examples: [ASSESSMENT_EXAMPLES.md](ASSESSMENT_EXAMPLES.md)
- Full Summary: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

### Created Files
- Database: `assessment_tables.sql`
- Service: `course_content_generator/app/services/assessment_service.py`
- Routes: `course_content_generator/app/routes_assessment.py`
- Templates: `course_content_generator/app/templates/student/`
  - `lesson_quiz.html`
  - `module_assessment.html`
  - `final_assessment.html`
  - `course_completion.html`

## 💻 Common Commands

### Check if specific tables exist
```bash
mysql -u root -p phosholi -e "SHOW TABLES LIKE 'quiz_%';"
```

### View quiz questions for a course
```bash
mysql -u root -p phosholi -e "SELECT * FROM quiz_questions WHERE course_id = 1;"
```

### Check student responses
```bash
mysql -u root -p phosholi -e "SELECT * FROM student_quiz_responses WHERE user_id = 1;"
```

### View certificates issued
```bash
mysql -u root -p phosholi -e "SELECT * FROM certificates;"
```

### Fix: Reset all assessment data (⚠️ deletes all)
```bash
mysql -u root -p phosholi << EOF
DELETE FROM student_quiz_responses;
DELETE FROM student_saq_responses;
DELETE FROM student_final_responses;
DELETE FROM certificates;
DELETE FROM course_completion_grades;
ALTER TABLE quiz_questions AUTO_INCREMENT = 1;
ALTER TABLE short_answer_questions AUTO_INCREMENT = 1;
EOF
```

## 🚨 Troubleshooting

### "Assessment blueprint not registered"
- Check your `run.py` or `__init__.py`
- Verify the import statement is present
- Restart Flask app

### "Table doesn't exist"
- Run: `mysql -u root -p phosholi < assessment_tables.sql`
- Check database name matches `phosholi`

### "Quiz questions not loading"
- Ensure assessments were created when course was saved
- Check quiz_questions table: `SELECT * FROM quiz_questions;`
- Verify course_id, module_index, lesson_index are correct

### "Styling looks broken"
- Clear browser cache (Ctrl+Shift+Del)
- Bootstrap CDN should be included in base template
- Check browser console for 404 errors

## 📚 What Each Component Does

| File | Purpose |
|------|---------|
| `assessment_tables.sql` | Database schema - import this first |
| `assessment_service.py` | Core business logic (grading, certificates, calculations) |
| `routes_assessment.py` | API endpoints (RESTful routes) |
| `lesson_quiz.html` | Student interface for taking quizzes |
| `module_assessment.html` | Student interface for SAQ submission |
| `final_assessment.html` | Student interface for final exam |
| `course_completion.html` | Results and certificate display |

## 🎓 Grading Structure

```
Final Grade = (Module Assessments × 40%) + (Final Assessment × 60%)

Certificate Threshold: 70%

Letter Grades:
A: 90-100%
B: 80-89%
C: 70-79%
D: 60-69%
F: Below 60%
```

## 🔑 Key Features

✅ **Automatic**
- Quiz grading
- Module score calculation
- Final grade calculation
- Certificate generation

✅ **Manual (Instructor)**
- SAQ grading with feedback
- Final assessment grading
- Score adjustments

✅ **Student Self-Service**
- Take quizzes
- Submit essays
- View scores
- Download certificates

## 📞 Need Help?

1. **Check logs**: Look at Flask console output
2. **Check database**: Verify tables and data exist
3. **Check templates**: Ensure templates load without 404 errors
4. **Check console**: Open browser DevTools F12 for JavaScript errors
5. **Read docs**: See ASSESSMENT_SYSTEM.md for detailed info

## 🎯 Next Steps After Setup

1. **Customize Questions**: Edit question generation in `assessment_service.py`
2. **Style Adjustments**: Modify CSS in template files
3. **Advanced Features**: Add time limits, question banks, etc.
4. **Analytics**: Create dashboard to view student performance
5. **Automation**: Set up email notifications for grades

## 💾 Database Backup Before Testing

```bash
# Backup your database
mysqldump -u root -p phosholi > backup_phosholi.sql

# If something goes wrong, restore:
mysql -u root -p phosholi < backup_phosholi.sql
```

---

**You're All Set! 🎉**

The assessment system is now installed and ready to use. Start by creating a course and testing the quiz, SAQ, and final assessment flows.

For detailed documentation, see:
- [Full System Documentation](ASSESSMENT_SYSTEM.md)
- [Integration Guide](ASSESSMENT_INTEGRATION.md)
- [Code Examples](ASSESSMENT_EXAMPLES.md)
