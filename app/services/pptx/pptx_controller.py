from app.services.llm_service import generate_pptx_content
from app.services.pptx.pptx_service import generate_presentation


def generate_lesson_pptx(course_title, module_title, lesson, preferences=None):

    slide_content = generate_pptx_content(
        course_title,
        module_title,
        lesson.get("title"),
        lesson.get("summary"),
        preferences
    )

    if not slide_content:
        return {"success": False, "message": "LLM failed"}

    result = generate_presentation(
        course_title,
        module_title,
        lesson.get("title"),
        slide_content
    )

    return result

