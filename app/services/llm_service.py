from groq import Groq
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")



# llm_service.py
def generate_speech(text):
    # Ensure variables exist
    if not VOICE_ID or not ELEVEN_API_KEY:
        raise Exception("Missing ElevenLabs Environment Variables (VOICE_ID or API_KEY)")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # More stable than monolingual_v1
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            # Log the actual error from ElevenLabs to your console
            print(f"ElevenLabs Error Details: {response.text}")
            raise Exception(f"ElevenLabs API Error: {response.status_code}")

        return response.content 
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error connecting to ElevenLabs: {str(e)}")

def generate_course(preferences: dict):
    """
    Generates fully structured LMS course JSON.
    Enforces required fields.
    """

    prompt = f"""
    Generate a COMPLETE professional course in STRICT JSON format.

    The JSON MUST contain EXACTLY these top-level keys:

    title
    domain
    level
    duration
    overview
    target_audience
    prerequisites
    learning_outcomes
    modules
    resources
    assessment
    certification

    STRUCTURE REQUIREMENTS:

    - learning_outcomes: array of 5 strings
    - modules: array of 5 objects
        Each module must contain:
            title (string)
            description (string)
            lessons (array of 3 objects)
                Each lesson must contain:
                    title (string)
                    summary (string)

    - resources: array of 5 objects
        Each resource must contain:
            title (string)
            author (string)
            url (string)

    - assessment: string
    - certification: string

    Course Details:
    Domain: {preferences.get("domain")}
    Topic: {preferences.get("topic")}
    Goal: {preferences.get("goal")}
    Level: {preferences.get("level")}
    Duration: {preferences.get("duration")}
    Learning Preference: {preferences.get("learning_preference")}
    Prior Knowledge: {preferences.get("prior_knowledge")}

    IMPORTANT:
    - Return ONLY valid JSON.
    - No markdown.
    - No explanation.
    - No extra text.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},  # 🔥 Enforced JSON mode
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional LMS curriculum architect that outputs strictly valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        json_output = response.choices[0].message.content

        return json.loads(json_output)

    except Exception as e:
        print("Groq API Error:", str(e))
        return None


def generate_lesson_notes(course_title, module_title, lesson_title, lesson_summary, preferences=None):
    """
    Generate detailed notes for a specific lesson using LLM
    
    Args:
        course_title: Title of the course
        module_title: Title of the module
        lesson_title: Title of the lesson
        lesson_summary: Brief summary of the lesson
        preferences: Optional learning preferences dict
    
    Returns:
        dict: Structured notes with introduction, key_concepts, examples, etc.
    """
    
    # Build personalization context if preferences available
    level_context = ""
    learning_style_context = ""
    
    if preferences:
        level = preferences.get('level', 'Beginner')
        learning_pref = preferences.get('learning_preference', 'Balanced Approach')
        
        level_context = f"""
        Target Level: {level}
        - Adjust complexity and depth accordingly
        - Use appropriate terminology for this level
        """
        
        learning_style_context = f"""
        Learning Preference: {learning_pref}
        - {'Focus on theoretical foundations and conceptual understanding' if 'Theory' in learning_pref else ''}
        - {'Emphasize practical applications and hands-on examples' if 'Practice' in learning_pref else ''}
        - {'Include visual descriptions and conceptual diagrams' if 'Visual' in learning_pref else ''}
        - {'Balance theory and practice' if 'Balanced' in learning_pref else ''}
        """
    
    prompt = f"""
    You are an expert educational content creator. Generate comprehensive, detailed lesson notes for the following:

    Course: {course_title}
    Module: {module_title}
    Lesson: {lesson_title}
    Lesson Summary: {lesson_summary}
    {level_context}
    {learning_style_context}
    
    Create structured notes that include:
    
    1. INTRODUCTION (2-3 paragraphs)
       - Overview of what will be covered
       - Why this topic is important
       - How it connects to the broader module
    
    2. KEY CONCEPTS (5-7 bullet points)
       - List the most important concepts/terms
       - Each should be clear and concise
    
    3. DETAILED EXPLANATION (400-600 words)
       - Comprehensive explanation of the lesson content
       - Break down complex ideas into understandable parts
       - Use analogies where helpful
       - Include real-world context
    
    4. EXAMPLES (2-3 detailed examples)
       - Practical applications of the concepts
       - Step-by-step walkthroughs
       - Code snippets or scenarios if applicable
    
    5. PRACTICE EXERCISES (3-5 exercises)
       - Questions or tasks to test understanding
       - Range from basic to advanced
       - Include both theoretical and practical problems
    
    6. SUMMARY (1-2 paragraphs)
       - Recap of main points
       - Key takeaways
       - Connection to next lessons
    
    7. ADDITIONAL RESOURCES (3-5 items)
       - Books, articles, videos, or websites
       - For further learning on this topic
    
    Return ONLY valid JSON with this exact structure:
    {{
        "introduction": "string",
        "key_concepts": ["concept 1", "concept 2", ...],
        "detailed_explanation": "string",
        "examples": ["example 1", "example 2", ...],
        "practice_exercises": ["exercise 1", "exercise 2", ...],
        "summary": "string",
        "additional_resources": ["resource 1", "resource 2", ...]
    }}
    
    IMPORTANT:
    - Return ONLY the JSON object
    - No markdown formatting
    - No additional text
    - Ensure all sections are comprehensive and educational
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content specialist that creates detailed, pedagogically sound lesson notes in JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        json_output = response.choices[0].message.content
        
        return json.loads(json_output)
        
    except Exception as e:
        print(f"LLM Notes Generation Error: {str(e)}")
        return None


# summary 
def summary_from(prompt, temperature=0.5, max_tokens=800):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI tutor that explains concepts clearly for students."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = response.choices[0].message.content

        if not content:
            raise Exception("Empty response from LLM")

        return content.strip()

    except Exception as e:
        raise Exception(f"Groq LLM Error: {str(e)}")

# llm_service.py
def generate_summary(prompt):
    # Replace this with your actual LLM call (OpenAI, etc.)
    response = summary_from(prompt)

    if not response:
        raise Exception("LLM returned empty response")

    return response

# explainer
def generate_explanation(prompt):
    response = summary_from(prompt, temperature=0.4, max_tokens=600)

    if not response:
        raise Exception("LLM returned empty explanation")

    return response


# ppt content generator
def generate_pptx_content(course_title, module_title, lesson_title, lesson_summary, preferences=None):
    """
    Generate structured PPTX slide content using LLM
    """

    level_context = ""
    if preferences:
        level_context = f"Target Level: {preferences.get('level', 'Beginner')}"

    prompt = f"""
    Generate a professional PowerPoint presentation in STRICT JSON format.

    Context:
    Course: {course_title}
    Module: {module_title}
    Lesson: {lesson_title}
    Summary: {lesson_summary}
    {level_context}

    REQUIRED STRUCTURE:

    {{
        "title": "Presentation title",
        "slides": [
            {{
                "type": "title",
                "title": "string",
                "subtitle": "string"
            }},
            {{
                "type": "bullet",
                "title": "string",
                "points": ["point 1", "point 2", "point 3", "point 4"]
            }},
            {{
                "type": "text",
                "title": "string",
                "content": "string"
            }}
        ]
    }}

    RULES:
    - Generate 6 to 8 slides total.
    - First slide MUST be type "title".
    - At least 4 slides must be type "bullet" or "text" with meaningful content.
    - Bullet slides must include 4-6 concise, relevant points.
    - Text slides must include a full paragraph summarizing a concept or example.
    - Use actual lesson-specific content, not generic placeholders.
    - Each slide should include useful educational content, not a single phrase.
    - Include at least one slide for "Why this matters" and one slide for "Key takeaway" or "Summary".
    - No markdown, no extra explanation, ONLY valid JSON.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert presentation designer that outputs strictly valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"PPTX Content Generation Error: {str(e)}")
        return None