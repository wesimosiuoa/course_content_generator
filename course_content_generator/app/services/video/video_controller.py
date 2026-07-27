"""
Video Controller
Orchestrates video generation from lesson content
"""

import os
from app.services.video.video_service import (
    generate_video,
    get_or_create_video,
    sanitize_filename,
    VIDEO_DIR,
    ensure_video_directory,
)


def generate_lesson_video(course_title, module_title, lesson, lesson_notes_path, pptx_path, preferences=None):
    """
    Generate a video for a lesson using notes and presentation.
    Always writes to VIDEO_DIR so the file is playable even if TTS falls back.
    """
    try:
        if not lesson_notes_path or not os.path.exists(lesson_notes_path):
            return {
                "success": False,
                "message": "Lesson notes file not found",
                "video_path": None,
            }

        if not pptx_path or not os.path.exists(pptx_path):
            return {
                "success": False,
                "message": "Presentation file not found",
                "video_path": None,
            }

        ensure_video_directory()
        lesson_title = (lesson or {}).get("title", "lesson")
        output_filename = (
            f"{sanitize_filename(course_title)}_"
            f"{sanitize_filename(module_title)}_"
            f"{sanitize_filename(lesson_title)}.mp4"
        )
        output_path = os.path.join(VIDEO_DIR, output_filename)

        course_info = {
            "course_title": course_title,
            "module_title": module_title,
            "lesson_title": lesson_title,
        }

        result = generate_video(
            lesson_notes_path,
            pptx_path,
            output_path,
            course_info,
        )
        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Error generating video: {str(e)}",
            "video_path": None,
        }
