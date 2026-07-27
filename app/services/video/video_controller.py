"""
Video Controller
Orchestrates video generation from lesson content
"""

from app.services.llm_service import generate_lesson_notes as llm_generate_notes
from app.services.video.video_service import (
    generate_video,
    get_or_create_video,
    sanitize_filename
)


def generate_lesson_video(course_title, module_title, lesson, lesson_notes_path, pptx_path, preferences=None):
    """
    Generate a video for a lesson using notes and presentation
    
    Args:
        course_title: Title of the course
        module_title: Title of the module
        lesson: Lesson dictionary with title and metadata
        lesson_notes_path: Path to lesson notes DOCX file
        pptx_path: Path to lesson presentation PPTX file
        preferences: User preferences dictionary
        
    Returns:
        dict: Video generation result with success status and metadata
    """
    
    try:
        # Validate input files exist
        import os
        if not os.path.exists(lesson_notes_path):
            return {
                "success": False,
                "message": "Lesson notes file not found",
                "video_path": None
            }
        
        if not os.path.exists(pptx_path):
            return {
                "success": False,
                "message": "Presentation file not found",
                "video_path": None
            }
        
        # Create output filename
        lesson_title = lesson.get("title", "lesson")
        output_filename = f"{sanitize_filename(course_title)}_{sanitize_filename(module_title)}_{sanitize_filename(lesson_title)}.mp4"
        
        # Generate video
        course_info = {
            "course_title": course_title,
            "module_title": module_title,
            "lesson_title": lesson_title
        }
        
        result = generate_video(lesson_notes_path, pptx_path, None, course_info)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error generating video: {str(e)}",
            "video_path": None
        }
