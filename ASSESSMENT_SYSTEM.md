# Assessment System Documentation

## Overview

This assessment system provides a comprehensive evaluation framework for the Course Generation platform with:
- **Lesson-end Quizzes** (Multiple Choice)
- **Module-end Short Answer Questions** (SAQ)
- **Final Assessment** (Essay/Long Answer)
- **Automatic Grading** for quizzes
- **Manual Grading** for SAQ and final assessments
- **Certificate Generation** for passing students (70%+)

## Grading Structure

### Weighting
- **Module Assessments**: 40%
  - Average of all module quiz + SAQ scores
- **Final Assessment**: 60%
  - Score on the final exam questions at end of course
  
### Passing Requirements
- **Certificate of Completion**: 70% weighted score
- **Module Quiz**: 60% to pass (not mandatory for course completion)
- **Letter Grades**:
  - A: 90-100%
  - B: 80-89%
  - C: 70-79%
  - D: 60-69%
  - F: Below 60%

## Database Schema

### Key Tables
1. **quiz_questions** - Lesson-end quiz questions
2. **quiz_answer_options** - Multiple choice options for quizzes
3. **student_quiz_responses** - Student quiz answers
4. **lesson_quiz_results** - Summary of lesson quiz performance
5. **short_answer_questions** - Module-end SAQ questions
6. **student_saq_responses** - Student SAQ submissions
7. **final_assessments** - Course-end final exam questions
8. **student_final_responses** - Student final exam submissions
9. **module_assessment_results** - Summary of module performance
10. **course_completion_grades** - Final grades and certificate status
11. **certificates** - Issued certificates

See `assessment_tables.sql` for full schema.

## API Endpoints

### Quiz Endpoints
- `GET /assessment/quiz/<course_id>/<module_index>/<lesson_index>` - Get quiz questions
- `POST /assessment/quiz/submit` - Submit quiz responses
- `GET /assessment/quiz/result/<course_id>/<module_index>/<lesson_index>` - Get quiz results

### SAQ Endpoints
- `GET /assessment/saq/<course_id>/<module_index>` - Get SAQ questions
- `POST /assessment/saq/submit` - Submit SAQ response
- `GET /assessment/saq/result/<course_id>/<module_index>` - Get SAQ results

### Final Assessment Endpoints
- `GET /assessment/final/<course_id>` - Get final assessment questions
- `POST /assessment/final/submit` - Submit final assessment
- `GET /assessment/final/results/<course_id>` - Get final assessment results

### Grading Endpoints
- `POST /assessment/grade/saq/<response_id>` - Grade SAQ response
- `POST /assessment/grade/final/<response_id>` - Grade final assessment

### Results & Certificate Endpoints
- `GET /assessment/completion/<course_id>` - Get completion status and grades
- `GET /assessment/certificate/<course_id>` - Get certificate info
- `POST /assessment/certificate/issue/<course_id>` - Issue certificate (instructor only)
- `POST /assessment/calculate/module/<course_id>/<module_index>` - Calculate module score
- `POST /assessment/calculate/final/<course_id>/<total_modules>` - Calculate final grade

## Usage Examples

### 1. Taking a Lesson Quiz

```javascript
// Fetch quiz questions
const response = await fetch('/assessment/quiz/1/0/0');
const data = await response.json();
// Display questions to student

// Submit responses
const payload = {
    course_id: 1,
    module_index: 0,
    lesson_index: 0,
    responses: [
        {question_id: 1, selected_option_id: 5},
        {question_id: 2, selected_option_id: 8}
    ]
};
const result = await fetch('/assessment/quiz/submit', {
    method: 'POST',
    body: JSON.stringify(payload)
});
```

### 2. Submitting Module Assessment

```javascript
// Fetch SAQ questions
const response = await fetch('/assessment/saq/1/0');
const data = await response.json();

// Submit answers
data.data.questions.forEach(question => {
    const answerText = document.getElementById(`answer_${question.id}`).value;
    fetch('/assessment/saq/submit', {
        method: 'POST',
        body: JSON.stringify({
            course_id: 1,
            module_index: 0,
            saq_id: question.id,
            answer_text: answerText
        })
    });
});
```

### 3. Grading SAQ Response

```javascript
const payload = {
    score: 8.5,
    feedback: "Great analysis! Could be more detailed."
};

const result = await fetch('/assessment/grade/saq/42', {
    method: 'POST',
    body: JSON.stringify(payload)
});
```

### 4. Calculating and Issuing Certificate

```javascript
// Calculate final grade
const gradeResult = await fetch('/assessment/calculate/final/1/4', {
    method: 'POST'
});
const gradeData = await gradeResult.json();

// Certificate is automatically issued if score >= 70%
if (gradeData.data.passed) {
    console.log('Certificate issued:', gradeData.data.certificate.certificate_code);
}
```

## Integration with Course Viewer

### Step 1: Register Blueprint in Flask App

In `app/__init__.py`:
```python
from .routes_assessment import assessment
app.register_blueprint(assessment)
```

### Step 2: Add Quiz Button to Lesson View

In lesson template, after lesson content:
```html
<a href="/templates/student/lesson_quiz.html?course={{ course.id }}&module={{ module_index }}&lesson={{ lesson_index }}" 
   class="btn btn-primary">
   📝 Take Quiz
</a>
```

### Step 3: Add SAQ Button to Module Summary

In module completion view:
```html
<a href="/templates/student/module_assessment.html?course={{ course.id }}&module={{ module_index }}" 
   class="btn btn-secondary">
   ✍️ Module Assessment
</a>
```

### Step 4: Add Final Assessment Button to Last Module

```html
<a href="/templates/student/final_assessment.html?course={{ course.id }}" 
   class="btn btn-warning btn-lg">
   🎯 Final Assessment (60% of Grade)
</a>
```

### Step 5: Show Completion Status

After course completion:
```html
<a href="/templates/student/course_completion.html?course={{ course.id }}" 
   class="btn btn-info btn-lg">
   📊 View Results & Certificate
</a>
```

## Grading Workflow

### For Instructors

1. **View Pending Responses**
   - Check admin dashboard for submissions needing grading

2. **Grade Short Answer Questions**
   ```
   POST /assessment/grade/saq/<response_id>
   {
       "score": 8.5,  // Out of 10
       "feedback": "Good work!"
   }
   ```

3. **Grade Final Assessment**
   ```
   POST /assessment/grade/final/<response_id>
   {
       "score": 18,  // Out of 20
       "feedback": "Excellent comprehensive answer"
   }
   ```

4. **Monitor Certificate Generation**
   - Certificates auto-issue when final grade >= 70%

## Question Generation

The system includes templates for auto-generating questions from course content. To customize:

### Modify Quiz Questions
Edit `assessment_service.py`, method `_generate_quiz_questions()`:
```python
def _generate_quiz_questions(self, lesson_title, lesson_summary, lesson_data):
    # Add your question generation logic here
    # Can integrate with LLM for custom questions
```

### Modify SAQ Questions
Edit `assessment_service.py`, method `_generate_saq_questions()`:
```python
def _generate_saq_questions(self, module_title, module_summary, module_data):
    # Add your SAQ generation logic here
```

### Modify Final Assessment Questions
Edit `assessment_service.py`, method `_generate_final_questions()`:
```python
def _generate_final_questions(self, course_data):
    # Add your final assessment generation logic here
```

## Security Considerations

1. **Session Validation** - All endpoints check if user is logged in
2. **TODO**: Add role-based access control for grading endpoints
3. **TODO**: Prevent quiz retakes after submission (configurable)
4. **TODO**: Add IP logging and proctoring features
5. **TODO**: Implement plagiarism detection for essays

## Performance Optimization

1. **Indexes** on frequently queried columns (user_id, course_id, module_index)
2. **Lazy Loading** - Don't fetch all assessments at once
3. **Caching** - Cache quiz results for quick retrieval
4. **Batch Processing** - Process multiple grades in parallel

## Future Enhancements

1. **Adaptive Testing** - Adjust difficulty based on performance
2. **Peer Review** - Students review each other's work
3. **Time Limits** - Add countdown timers for quizzes
4. **Question Banks** - Randomize questions from banks
5. **Certificate PDF** - Generate beautiful certificate PDFs
6. **Plagiarism Detection** - Turnitin/Copyscape integration
7. **Analytics Dashboard** - Detailed performance analytics
8. **Retake Manager** - Allow limited retakes with score averaging
9. **Bonus Questions** - Extra credit for top performers
10. **Rubric Manager** - Visual rubric builder for graders

## Template Files

- `lesson_quiz.html` - Student quiz interface
- `module_assessment.html` - Module SAQ interface  
- `final_assessment.html` - Final exam interface
- `course_completion.html` - Results and certificate display

## Troubleshooting

### Issue: Quiz not loading
- Check course_id, module_index, lesson_index parameters
- Verify quiz questions exist in database
- Check browser console for errors

### Issue: Responses not submitting
- Ensure all questions are answered
- Check network tab for API response status
- Verify user is logged in (session check)

### Issue: Grade calculation incorrect
- Check that all module assessments are completed
- Verify SAQ responses are graded (is_graded = 1)
- Check final assessment responses are graded

### Issue: Certificate not issued
- Verify final score >= 70%
- Ensure `calculate_final_grade()` was called
- Check certificates table for entries

## Support

For questions or issues with the assessment system, contact the development team or file an issue on the project repository.
