from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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