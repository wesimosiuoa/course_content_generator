# LLM-Based Assessment System

## Overview

The assessment system now integrates with Groq's LLM API (using Claude via llama-3.3-70b-versatile model) to:
- **Generate intelligent quiz questions** from lesson content
- **Generate thoughtful short answer questions** from module content
- **Generate comprehensive essay questions** for final assessments
- **Auto-grade essays and short answers** using LLM evaluation

## How It Works

### 1. Question Generation

When a course is saved, the system automatically generates assessments using the LLM:

#### Quiz Generation
```
Lesson Content → LLM → 4-5 Multiple Choice Questions
```
- Questions are context-aware and specific to lesson content
- Includes plausible wrong answers
- Automatically identifies correct answers

#### SAQ Generation
```
Module Content + All Lessons → LLM → 2-3 Short Answer Questions
```
- Questions test critical thinking, not memorization
- Includes grading rubrics automatically
- Appropriate difficulty level

#### Final Assessment Generation
```
Course Overview + All Modules → LLM → 3-4 Essay Questions
```
- Comprehensive questions testing synthesis of concepts
- Includes guidance on what constitutes a complete answer
- Key concepts students should address

### 2. LLM-Based Grading

#### Essay Grading
```
Student Answer + Question + Rubric → LLM → Score + Detailed Feedback
```

The system evaluates:
- **Comprehensiveness** - Covers all main topics
- **Critical Thinking** - Shows analysis and synthesis
- **Clarity** - Well-organized and clear presentation
- **Evidence** - Supports claims with examples
- **Depth** - Demonstrates genuine understanding

Outputs:
- Numerical score out of max
- Confidence level (0.0-1.0)
- Detailed feedback
- Strengths and areas for improvement

## API Endpoints

### Question Generation (Automatic)

These are called automatically when a course is saved. No manual API calls needed.

```
POST /save_course
├─ Creates quiz questions for each lesson
├─ Creates SAQ questions for each module
└─ Creates final assessment questions for course
```

### LLM-Based Grading Endpoints

#### Grade SAQ with LLM Suggestion
```
POST /assessment/llm/grade-saq/<response_id>

Response:
{
    "status": "success",
    "data": {
        "score": 8.5,
        "score_out_of": 10,
        "feedback": "Detailed feedback text...",
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["area 1", "area 2"],
        "confidence": 0.92
    }
}
```

#### Grade Final Assessment with LLM Suggestion
```
POST /assessment/llm/grade-final/<response_id>

Response:
{
    "status": "success",
    "data": {
        "score": 18,
        "score_out_of": 20,
        "criteria": {
            "comprehensiveness": {"rating": 5, "comment": "..."},
            "critical_thinking": {"rating": 4, "comment": "..."},
            "clarity": {"rating": 5, "comment": "..."},
            "evidence": {"rating": 4, "comment": "..."},
            "depth": {"rating": 4, "comment": "..."}
        },
        "overall_feedback": "...",
        "strengths": ["strength 1"],
        "improvements": ["improvement 1"],
        "confidence": 0.88
    }
}
```

#### Apply LLM Grade (Save the suggested grade)
```
POST /assessment/llm/apply-grade/<response_id>/<response_type>

Body:
{
    "score": 8.5,
    "feedback": "Feedback text from LLM"
}

response_type: "saq" or "final"
```

## Integration in Your Application

### 1. Automatic Question Generation

When saving a course, questions are automatically generated:

```python
# In app/routes.py when saving a course

from app.services.assessment_service import assessment_service

course_data = session.get('generated_course')
course_id = save_to_database(course_data)

# Assessments are automatically created with LLM
modules = course_data.get('modules', [])

for module_idx, module in enumerate(modules):
    # LLM generates SAQ questions
    assessment_service.create_saq_for_module(course_id, module_idx, module)
    
    for lesson_idx, lesson in enumerate(module.get('lessons', [])):
        # LLM generates quiz questions
        assessment_service.create_quiz_for_lesson(
            course_id, module_idx, lesson_idx, lesson
        )

# LLM generates final assessment questions
assessment_service.create_final_assessment(course_id, course_data)
```

### 2. Instructor Grading with LLM Suggestions

Create a grading interface that uses LLM suggestions:

```html
<!-- Grading Dashboard -->
<div class="saq-response">
    <h5>Short Answer Response</h5>
    <p class="student-answer">{{ response.answer_text }}</p>
    
    <button class="btn btn-primary" onclick="getSuggestion({{ response.id }}, 'saq')">
        💡 Get LLM Suggestion
    </button>
    
    <div id="llm-suggestion" style="display:none;">
        <div class="alert alert-info">
            <h6>LLM Suggested Grade: <span id="suggested-score"></span>/10</h6>
            <p>Confidence: <span id="confidence"></span></p>
            <p id="feedback"></p>
            <button onclick="acceptSuggestion({{ response.id }})">
                ✓ Accept & Save
            </button>
        </div>
    </div>
    
    <!-- Manual grading form -->
    <form>
        <input type="number" placeholder="Score out of 10" min="0" max="10" step="0.5">
        <textarea placeholder="Feedback"></textarea>
        <button type="submit">Save Grade</button>
    </form>
</div>

<script>
function getSuggestion(responseId, type) {
    fetch(`/assessment/llm/grade-${type}/${responseId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById('suggested-score').textContent = data.data.score;
        document.getElementById('confidence').textContent = 
            (data.data.confidence * 100).toFixed(0) + '%';
        document.getElementById('feedback').textContent = data.data.feedback;
        document.getElementById('llm-suggestion').style.display = 'block';
    });
}

function acceptSuggestion(responseId) {
    const score = document.getElementById('suggested-score').textContent;
    const feedback = document.getElementById('feedback').textContent;
    
    fetch(`/assessment/llm/apply-grade/${responseId}/saq`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({score, feedback})
    })
    .then(r => r.json())
    .then(data => {
        alert('Grade saved successfully!');
        // Refresh page or update UI
    });
}
</script>
```

## Configuration

### LLM Settings (in assessment_service.py)

```python
# Temperature controls creative vs consistent output
# Lower = more consistent (better for grading)
# Higher = more varied (better for question generation)

# Quiz generation: temperature=0.6
# SAQ generation: temperature=0.6
# Final assessment: temperature=0.6
# Grading: temperature=0.4 (more strict/consistent)
```

### Prompt Customization

Edit the prompt strings in these methods to customize question/grading style:
- `_generate_quiz_questions()` - Quiz question prompts
- `_generate_saq_questions()` - SAQ question prompts  
- `_generate_final_questions()` - Final assessment prompts
- `llm_grade_saq_response()` - SAQ grading prompt
- `llm_grade_final_response()` - Essay grading prompt

## Benefits of LLM-Based Assessment

### For Students
✅ Varied, relevant questions specific to course content
✅ Challenging but fair assessment
✅ Detailed feedback on essay responses
✅ Fair grading standards
✅ More engaging learning experience

### For Instructors
✅ Automated question generation (saves time)
✅ Instant grading suggestions for essays
✅ Consistent evaluation criteria
✅ Detailed feedback for all responses
✅ More time to focus on student needs

### For Institution
✅ Scalable assessment system
✅ Consistent quality across courses
✅ Reduced grading burden
✅ Rich data for learning analytics
✅ Improved student learning outcomes

## Limitations and Cautions

1. **LLM Consistency**: While consistent at temp=0.4, LLM grading may vary slightly between runs
2. **Subjectivity**: LLM may interpret rubrics differently than intended
3. **Bias**: Consider potential biases in model training
4. **No Perfect Accuracy**: Always review critical grades
5. **Context Limitations**: Long essays may truncate or lose context

## Best Practices

1. **Review First Responses**: Check LLM grading quality on initial assessments
2. **Set Standards**: Adjust prompts until LLM matches your standards
3. **Confidence Scores**: Pay attention to confidence levels (<0.75 = review manually)
4. **Human Oversight**: Use LLM suggestions, don't automate final grades
5. **Feedback Quality**: Review feedback messages for accuracy

## Fallback Behavior

If LLM API fails (rate limit, connectivity, etc.):
- **Question Generation**: Falls back to basic template questions
- **Grading**: Returns error - instructor must grade manually
- **No Impact on System**: Assessment system continues to function

## Environment Requirements

The system requires:
```
GROQ_API_KEY=your_key_here
```

This should already be set in your `.env` file since you're using Groq for course generation.

## Advanced Features

### Custom Grading Rubrics

When creating a course with custom rubrics:

```python
# In the SAQ prompt, include custom rubric requirements
rubric = {
    "technical_accuracy": "Code runs without errors, logic is sound",
    "code_quality": "Clean, well-commented, follows best practices",
    "explanation": "Clear explanation of approach and implementation",
    "creativity": "Goes beyond requirements, shows initiative"
}
```

### Adaptive Question Difficulty

Modify the LLM prompt to adjust difficulty:

```python
# For beginner courses
prompt += "\nGenerate BEGINNER LEVEL questions focusing on fundamental concepts."

# For advanced courses
prompt += "\nGenerate ADVANCED LEVEL questions requiring synthesis and critical analysis."
```

### Multi-Language Support

The LLM can generate questions in any language:

```python
prompt += f"\nGenerate questions in {language}."
```

## Monitoring and Analytics

### Grade Distribution
Track grade statistics to ensure appropriate difficulty:
```sql
SELECT 
    COUNT(*) as responses,
    AVG(score) as avg_score,
    MIN(score) as min_score,
    MAX(score) as max_score,
    AVG(confidence) as avg_confidence
FROM student_saq_responses
WHERE is_graded = 1
GROUP BY saq_id;
```

### LLM Confidence
Monitor how confident the LLM is in its gradings:
- <0.7: Review manually
- 0.7-0.85: Can rely on LLM
- >0.85: High confidence in grade

## Troubleshooting

### Issue: "API Error" when generating questions
- Check GROQ_API_KEY is set
- Check API rate limits
- Verify internet connection
- System falls back to template questions

### Issue: LLM grades seem inconsistent
- Check temperature settings (should be 0.4 for grading)
- Some variation is normal
- Review confidence scores
- Check for prompt ambiguity

### Issue: LLM grading doesn't match rubric
- Review and refine grading prompt
- Ensure rubric is clearly described in prompt
- Test with sample responses first
- Adjust prompt language/examples

### Issue: Grades too lenient/strict
- Adjust prompt to include scoring guidelines
- Add examples of what different scores mean
- Specify what constitutes "excellent", "good", "fair", etc.

## Example Workflow

```
1. Instructor creates course in UI
2. System auto-generates assessments with LLM
3. Students take quizzes (auto-graded)
4. Students submit essays/SAQ
5. Instructor views pending responses
6. Instructor clicks "Get LLM Suggestion"
7. LLM analyzes response and returns:
   - Suggested score with confidence
   - Detailed feedback
   - Strengths and weaknesses
8. Instructor reviews suggestion
9. Instructor accepts or modifies grade
10. Grade and feedback saved to database
11. Student views grade and detailed feedback
12. Final grades calculated automatically
13. Certificates issued for those who passed
```

## Performance Considerations

- **Question Generation**: ~5-10 seconds per course (done once)
- **Grading Suggestion**: ~10-20 seconds per response (on demand)
- **Caching**: Could cache similar responses for faster grading

## Future Enhancements

1. **Batch Grading**: Grade all pending responses in one call
2. **Rubric Learning**: LLM learns specific rubric preferences
3. **Plagiarism Detection**: LLM checks for potential plagiarism
4. **Hint Generation**: LLM generates hints during quizzes
5. **Adaptive Questions**: Difficulty increases with performance
6. **Multi-Modal**: Support images, code, diagrams in assessments
7. **Real-time Feedback**: Immediate feedback during quiz
8. **Analytics Dashboard**: Visualized grading distributions

## Support

For issues or questions:
- Check error messages in Flask console
- Review API usage in Groq dashboard
- Test with simple questions first
- Check documentation in code comments
