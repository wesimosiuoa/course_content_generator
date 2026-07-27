"""
PPTX Generation Service
Creates PowerPoint presentations from structured LLM content
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
import os
from datetime import datetime

PPTX_DIR = os.path.join(os.path.dirname(__file__), 'presentations')

# Professional color scheme
COLOR_PRIMARY = RGBColor(25, 103, 210)      # Professional blue
COLOR_DARK = RGBColor(30, 40, 60)            # Dark navy
COLOR_ACCENT = RGBColor(66, 133, 244)       # Bright blue
COLOR_TEXT = RGBColor(50, 50, 50)            # Dark gray
COLOR_LIGHT_BG = RGBColor(245, 248, 252)    # Light blue background
COLOR_WHITE = RGBColor(255, 255, 255)       # White


def ensure_pptx_directory():
    if not os.path.exists(PPTX_DIR):
        os.makedirs(PPTX_DIR)
    return PPTX_DIR


def sanitize_filename(text):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    return text.replace(' ', '_').lower()[:50]


def generate_presentation(course_title, module_title, lesson_title, slide_content):
    """
    Create professional PPTX from structured slide JSON with modern styling
    """

    try:
        # Create presentation with 16:9 aspect ratio
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

        for idx, slide_data in enumerate(slide_content.get("slides", [])):
            slide_type = slide_data.get("type")

            if slide_type == "title":
                # Title slide with gradient background effect
                slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
                
                # Add background shape (full slide color)
                background = slide.shapes.add_shape(
                    1,  # Rectangle
                    0, 0,
                    prs.slide_width,
                    prs.slide_height
                )
                background.fill.solid()
                background.fill.fore_color.rgb = COLOR_PRIMARY
                background.line.color.rgb = COLOR_PRIMARY
                
                # Add white accent bar
                accent = slide.shapes.add_shape(
                    1,  # Rectangle
                    0, Inches(3.5),
                    prs.slide_width,
                    Inches(2.125)
                )
                accent.fill.solid()
                accent.fill.fore_color.rgb = COLOR_WHITE
                accent.line.color.rgb = COLOR_WHITE
                
                # Add title
                title_box = slide.shapes.add_textbox(
                    Inches(0.5), Inches(1.5),
                    Inches(9), Inches(2)
                )
                title_frame = title_box.text_frame
                title_frame.word_wrap = True
                title_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                
                title_p = title_frame.paragraphs[0]
                title_p.text = slide_data.get("title", "")
                title_p.font.size = Pt(54)
                title_p.font.bold = True
                title_p.font.color.rgb = COLOR_WHITE
                title_p.alignment = PP_ALIGN.CENTER
                
                # Add subtitle
                subtitle_box = slide.shapes.add_textbox(
                    Inches(0.5), Inches(3.7),
                    Inches(9), Inches(1.5)
                )
                subtitle_frame = subtitle_box.text_frame
                subtitle_frame.word_wrap = True
                
                subtitle_p = subtitle_frame.paragraphs[0]
                subtitle_p.text = slide_data.get("subtitle", "")
                subtitle_p.font.size = Pt(28)
                subtitle_p.font.color.rgb = COLOR_PRIMARY
                subtitle_p.alignment = PP_ALIGN.CENTER

            elif slide_type in ("bullet", "text"):
                # Content slide with professional design
                slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
                
                # Add background
                background = slide.shapes.add_shape(
                    1,  # Rectangle
                    0, 0,
                    prs.slide_width,
                    prs.slide_height
                )
                background.fill.solid()
                background.fill.fore_color.rgb = COLOR_WHITE
                background.line.color.rgb = COLOR_WHITE
                
                # Add header bar
                header = slide.shapes.add_shape(
                    1,  # Rectangle
                    0, 0,
                    prs.slide_width,
                    Inches(0.8)
                )
                header.fill.solid()
                header.fill.fore_color.rgb = COLOR_PRIMARY
                header.line.color.rgb = COLOR_PRIMARY
                
                # Add left accent mark
                accent_mark = slide.shapes.add_shape(
                    1,  # Rectangle
                    0, Inches(0.8),
                    Inches(0.08),
                    Inches(4.825)
                )
                accent_mark.fill.solid()
                accent_mark.fill.fore_color.rgb = COLOR_ACCENT
                accent_mark.line.color.rgb = COLOR_ACCENT
                
                # Add title in header
                title_box = slide.shapes.add_textbox(
                    Inches(0.5), Inches(0.15),
                    Inches(9), Inches(0.5)
                )
                title_frame = title_box.text_frame
                title_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                
                title_p = title_frame.paragraphs[0]
                title_p.text = slide_data.get("title", "")
                title_p.font.size = Pt(40)
                title_p.font.bold = True
                title_p.font.color.rgb = COLOR_WHITE
                
                # Add slide number in header
                slide_num_box = slide.shapes.add_textbox(
                    Inches(8.5), Inches(0.2),
                    Inches(1.2), Inches(0.4)
                )
                slide_num_frame = slide_num_box.text_frame
                slide_num_p = slide_num_frame.paragraphs[0]
                slide_num_p.text = f"{idx + 1}"
                slide_num_p.font.size = Pt(16)
                slide_num_p.font.color.rgb = COLOR_WHITE
                
                # Add content
                content_box = slide.shapes.add_textbox(
                    Inches(0.7), Inches(1.2),
                    Inches(8.6), Inches(4)
                )
                content_frame = content_box.text_frame
                content_frame.word_wrap = True
                
                points = slide_data.get("points", [])
                content = slide_data.get("content", "")
                
                if points:
                    # Bullet points
                    first = True
                    for point in points:
                        if first:
                            p = content_frame.paragraphs[0]
                            first = False
                        else:
                            p = content_frame.add_paragraph()
                        
                        p.text = point
                        p.font.size = Pt(20)
                        p.font.color.rgb = COLOR_TEXT
                        p.level = 0
                        p.space_before = Pt(10)
                        p.space_after = Pt(10)
                else:
                    # Text content
                    p = content_frame.paragraphs[0]
                    p.text = content
                    p.font.size = Pt(18)
                    p.font.color.rgb = COLOR_TEXT
                    p.line_spacing = 1.5
                    p.space_after = Pt(12)

        # Save file
        ensure_pptx_directory()

        filename = f"{sanitize_filename(course_title)}_{sanitize_filename(module_title)}_{sanitize_filename(lesson_title)}.pptx"
        file_path = os.path.join(PPTX_DIR, filename)

        prs.save(file_path)

        return {
            "success": True,
            "file_path": file_path,
            "message": "Professional PPTX generated successfully"
        }

    except Exception as e:
        print(f"PPTX Generation Error: {str(e)}")
        return {
            "success": False,
            "file_path": None,
            "message": str(e)
        }