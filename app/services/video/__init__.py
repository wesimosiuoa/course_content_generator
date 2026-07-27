"""
Video Service Module
Handles video generation from lesson notes and presentations
"""

from .video_service import (
    generate_video,
    get_or_create_video,
    list_generated_videos,
    delete_video,
    ensure_video_directory,
    VIDEO_DIR
)

from .video_controller import (
    generate_lesson_video
)

__all__ = [
    'generate_video',
    'get_or_create_video',
    'list_generated_videos',
    'delete_video',
    'ensure_video_directory',
    'VIDEO_DIR',
    'generate_lesson_video'
]
