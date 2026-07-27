from app.services.llm_service import generate_pptx_content
from app.services.pptx.pptx_service import generate_presentation, normalize_slide_content, build_fallback_slides


def generate_lesson_pptx(course_title, module_title, lesson, preferences=None):
    """
    Build PPTX for a lesson.
    Uses LLM when available; always falls back to structured multi-slide content
    so presentations are never a single empty line.
    """
    lesson = lesson or {}
    lesson_title = lesson.get("title") or "Lesson"
    lesson_summary = (
        lesson.get("summary")
        or lesson.get("description")
        or ""
    )
    lesson_content = (
        lesson.get("content")
        or lesson.get("body")
        or lesson.get("notes")
        or lesson_summary
    )

    slide_content = generate_pptx_content(
        course_title,
        module_title,
        lesson_title,
        lesson_summary,
        preferences,
        lesson_content=lesson_content,
    )

    if not slide_content or not isinstance(slide_content, dict):
        print("LLM PPTX content missing — using fallback slides")
        slide_content = build_fallback_slides(
            course_title, module_title, lesson_title, lesson_summary, lesson_content
        )
    else:
        slide_content = normalize_slide_content(
            slide_content,
            course_title=course_title,
            module_title=module_title,
            lesson_title=lesson_title,
            lesson_summary=lesson_summary,
            lesson_content=lesson_content,
        )

    result = generate_presentation(
        course_title,
        module_title,
        lesson_title,
        slide_content,
    )

    return result
