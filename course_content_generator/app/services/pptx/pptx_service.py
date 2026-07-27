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


def _split_into_points(text, max_points=6, min_words=6):
    """Turn free text into bullet-friendly points."""
    if not text:
        return []
    raw = str(text).replace("\r", "\n")
    chunks = []
    for line in raw.split("\n"):
        line = line.strip(" -\t•*")
        if line:
            chunks.append(line)
    if len(chunks) <= 1:
        # sentence split
        import re
        parts = re.split(r'(?<=[.!?])\s+', str(text).strip())
        chunks = [p.strip() for p in parts if p and p.strip()]

    points = []
    for c in chunks:
        if len(c.split()) < min_words and points:
            points[-1] = f"{points[-1]} {c}".strip()
        else:
            points.append(c)
        if len(points) >= max_points:
            break
    return points


def build_fallback_slides(course_title, module_title, lesson_title, lesson_summary="", lesson_content=""):
    """
    Deterministic multi-slide deck when LLM fails or returns thin content.
    """
    body = (lesson_content or lesson_summary or "").strip()
    summary = (lesson_summary or body[:280] or f"Overview of {lesson_title}.").strip()
    points = _split_into_points(body, max_points=6) or [
        f"Understand the core idea of {lesson_title}.",
        f"Connect {lesson_title} to the goals of {module_title}.",
        f"Identify practical applications of {lesson_title}.",
        f"Review key terms and definitions for {lesson_title}.",
        f"Apply {lesson_title} concepts in a simple example.",
        f"Reflect on how {lesson_title} supports the course {course_title}.",
    ]
    if len(points) < 4:
        points = (points + [
            f"Discuss challenges related to {lesson_title}.",
            f"Summarize the main takeaways from {lesson_title}.",
            f"Plan next steps after learning {lesson_title}.",
            f"Relate {lesson_title} to real-world practice.",
        ])[:6]

    mid = max(1, len(points) // 2)
    return {
        "title": lesson_title,
        "slides": [
            {
                "type": "title",
                "title": lesson_title,
                "subtitle": f"{module_title} · {course_title}",
            },
            {
                "type": "bullet",
                "title": "Learning objectives",
                "points": points[:4],
            },
            {
                "type": "text",
                "title": "Lesson overview",
                "content": summary if len(summary.split()) >= 20 else (
                    f"{summary} This lesson covers essential ideas in {lesson_title} "
                    f"within {module_title}, preparing you to apply the concepts confidently."
                ),
            },
            {
                "type": "bullet",
                "title": f"Key ideas in {lesson_title}",
                "points": points[:5],
            },
            {
                "type": "bullet",
                "title": "Why this matters",
                "points": [
                    f"Mastering {lesson_title} strengthens understanding of {module_title}.",
                    f"These skills transfer to related topics across {course_title}.",
                    "Clear foundations reduce mistakes when tackling advanced work.",
                    "Practical awareness helps you evaluate real examples more carefully.",
                ],
            },
            {
                "type": "bullet",
                "title": "Practice focus",
                "points": points[mid:mid + 4] if points[mid:] else points[:4],
            },
            {
                "type": "bullet",
                "title": "Key takeaways",
                "points": [
                    f"Recall the main definitions and steps in {lesson_title}.",
                    "Explain the concept in your own words with one example.",
                    "Identify when and why the approach should be used.",
                    "Prepare questions for review or assessment on this lesson.",
                ],
            },
        ],
    }


def normalize_slide_content(slide_content, course_title="", module_title="", lesson_title="",
                            lesson_summary="", lesson_content=""):
    """
    Ensure slides have usable multi-line content (fix empty / 1-line decks).
    """
    if not slide_content or not isinstance(slide_content, dict):
        return build_fallback_slides(
            course_title, module_title, lesson_title, lesson_summary, lesson_content
        )

    slides = slide_content.get("slides") or slide_content.get("Slides") or []
    if not isinstance(slides, list):
        slides = []

    normalized = []
    for s in slides:
        if not isinstance(s, dict):
            continue
        stype = (s.get("type") or s.get("slide_type") or "bullet").lower().strip()
        if stype in ("title_slide", "cover"):
            stype = "title"
        if stype in ("bullets", "list", "content", "objectives"):
            stype = "bullet"
        if stype in ("paragraph", "body", "section"):
            stype = "text"

        title = (s.get("title") or s.get("heading") or "Slide").strip()
        points = s.get("points") or s.get("bullets") or s.get("items") or []
        if isinstance(points, str):
            points = _split_into_points(points)
        points = [str(p).strip() for p in points if str(p).strip()]
        content = (s.get("content") or s.get("text") or s.get("body") or "").strip()

        if stype == "title":
            normalized.append({
                "type": "title",
                "title": title or lesson_title or "Lesson",
                "subtitle": (s.get("subtitle") or f"{module_title} · {course_title}").strip(),
            })
            continue

        # Expand thin bullet/text slides
        if stype == "bullet":
            if len(points) < 3:
                extra = _split_into_points(content or lesson_content or lesson_summary)
                for e in extra:
                    if e not in points:
                        points.append(e)
                    if len(points) >= 4:
                        break
            if len(points) < 3:
                points = (points + [
                    f"Explore the main idea of {title}.",
                    f"Connect {title} to {lesson_title or 'this lesson'}.",
                    f"Apply {title} with a short practical example.",
                    f"Review and summarize {title} in your own words.",
                ])[:5]
            normalized.append({"type": "bullet", "title": title, "points": points[:6]})
        else:
            if len(content.split()) < 20:
                filler = lesson_summary or lesson_content or ""
                content = (
                    f"{content} {filler}".strip()
                    or f"This section explains {title} in the context of {lesson_title}."
                )
                if len(content.split()) < 20:
                    content = (
                        f"{content} Focus on understanding the concept, recognizing examples, "
                        f"and applying it within {module_title or 'the module'}."
                    )
            # Prefer bullets when content is list-like
            maybe_points = _split_into_points(content)
            if len(maybe_points) >= 4 and all(len(p.split()) < 40 for p in maybe_points[:4]):
                normalized.append({
                    "type": "bullet",
                    "title": title,
                    "points": maybe_points[:6],
                })
            else:
                normalized.append({"type": "text", "title": title, "content": content})

    # Too few slides → merge with fallback structure
    if len(normalized) < 4:
        fallback = build_fallback_slides(
            course_title, module_title, lesson_title, lesson_summary, lesson_content
        )
        # keep title from LLM if present
        title_slides = [s for s in normalized if s.get("type") == "title"]
        content_slides = [s for s in normalized if s.get("type") != "title"]
        fb_content = [s for s in fallback["slides"] if s.get("type") != "title"]
        merged = title_slides[:1] or [fallback["slides"][0]]
        merged.extend(content_slides)
        for s in fb_content:
            if len(merged) >= 7:
                break
            merged.append(s)
        normalized = merged

    slide_content = dict(slide_content)
    slide_content["title"] = slide_content.get("title") or lesson_title or "Presentation"
    slide_content["slides"] = normalized
    return slide_content


def generate_presentation(course_title, module_title, lesson_title, slide_content):
    """
    Create professional PPTX from structured slide JSON with modern styling
    """

    try:
        slide_content = normalize_slide_content(
            slide_content or {},
            course_title=course_title,
            module_title=module_title,
            lesson_title=lesson_title,
        )

        # Create presentation with 16:9 aspect ratio
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

        slides_list = slide_content.get("slides", [])
        if not slides_list:
            slides_list = build_fallback_slides(
                course_title, module_title, lesson_title
            )["slides"]

        for idx, slide_data in enumerate(slides_list):
            slide_type = (slide_data.get("type") or "bullet").lower()

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
                
                points = slide_data.get("points") or []
                content = (slide_data.get("content") or "").strip()
                if isinstance(points, str):
                    points = [points]
                points = [str(p).strip() for p in points if str(p).strip()]

                # Never leave a blank content slide
                if not points and not content:
                    content = f"Key ideas for: {slide_data.get('title') or lesson_title or 'this topic'}."
                    points = [
                        content,
                        f"Review related concepts from {module_title or 'the module'}.",
                        f"Practice applying ideas from {lesson_title or 'the lesson'}.",
                    ]

                if points:
                    first = True
                    for point in points:
                        if first:
                            p = content_frame.paragraphs[0]
                            first = False
                        else:
                            p = content_frame.add_paragraph()

                        # Explicit bullet prefix so export/video extract multi-line text
                        clean = point.lstrip("•-* ").strip()
                        p.text = f"• {clean}"
                        p.font.size = Pt(18)
                        p.font.color.rgb = COLOR_TEXT
                        p.level = 0
                        p.space_before = Pt(8)
                        p.space_after = Pt(8)
                else:
                    p = content_frame.paragraphs[0]
                    p.text = content
                    p.font.size = Pt(17)
                    p.font.color.rgb = COLOR_TEXT
                    p.line_spacing = 1.35
                    p.space_after = Pt(10)

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