
import os
import json
import requests
from dotenv import load_dotenv

from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    app_dir = Path(sys.executable).parent
else:
    app_dir = Path(__file__).resolve().parent

load_dotenv(app_dir / ".env")

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "apac.amazon.nova-lite-v1:0"
)


def generate_narratives(strengths, improvements, competency_questions):
    """
    strengths/improvements format:
    [{"competency": "Customer Focus", "score": 3.8}]

    competency_questions format:
    {
        "Customer Focus": [
            "Question text 1",
            "Question text 2"
        ]
    }
    """

    fallback = {
        "strengths": {
            item["competency"]:
                (
                    f"{item['competency']} is a relative strength "
                    "based on the calculated feedback scores."
                )
            for item in strengths
        },
        "improvements": {
            item["competency"]:
                (
                    f"{item['competency']} may be a useful area "
                    "for further development based on the "
                    "calculated feedback scores."
                )
            for item in improvements
        },
    }

    api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

    if not api_key:
        print("Bedrock API key not found. Using fallback narratives.")
        return fallback

    # Keep only questions related to selected competencies.
    selected_competencies = {
        item["competency"] for item in strengths + improvements
    }

    relevant_questions = {
        competency: competency_questions.get(competency, [])
        for competency in selected_competencies
    }

    prompt = f"""
You are a professional workplace feedback report writer.

Generate narratives for the selected strengths and improvement areas
using only the supplied competency names, calculated scores, and
assessment questions.

STRENGTHS:
{json.dumps(strengths, ensure_ascii=False)}

IMPROVEMENT AREAS:
{json.dumps(improvements, ensure_ascii=False)}

COMPETENCY QUESTIONS:
{json.dumps(relevant_questions, ensure_ascii=False)}

Return ONLY valid JSON in this format:
{{
    "strengths": {{
        "competency name": "Narrative"
    }},
    "improvements": {{
        "competency name": "Narrative"
    }}
}}

NARRATIVE REQUIREMENTS:

1. Write 4-5 complete sentences for each competency, aiming for
   approximately 70-100 words per narrative.
2. Explain what the competency means in a relevant workplace context.
3. Interpret scores cautiously. A score indicates a relative
   feedback rating, not proof of specific employee behaviour.
4. Use the supplied questions to understand what the competency
   measures. Do not treat the questions as evidence of behaviour.
5. Do not claim that the employee demonstrated, consistently
   performed, achieved, or failed at anything unless actual
   supporting evidence has been supplied.
6. Do not invent incidents, achievements, reviewer comments,
   outcomes, or personal characteristics.
7. For strengths, explain how the competency could be maintained
   and developed further without assuming the employee already
   performs specific actions.
8. For improvement areas, suggest practical ways to develop the
   competency without assuming the employee has a particular
   weakness beyond the score-based relative rating.
9. Make the narratives specific to each competency and its questions.
10. Use professional, constructive, non-repetitive language.
11. Do not generate recommendations as a separate section.
12. Include every supplied competency exactly once in its
    corresponding section.
13. Return valid JSON only. Do not use Markdown fences or add
    text outside the JSON object.
"""

    url = (
        f"https://bedrock-runtime.{AWS_REGION}.amazonaws.com"
        f"/model/{MODEL_ID}/converse"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        "inferenceConfig": {
            "maxTokens": 2500,
            "temperature": 0.2,
        },
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        text = result["output"]["message"]["content"][0]["text"].strip()

        # Remove Markdown fences if the model adds them.
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3].strip()

        generated = json.loads(text)

        for section in ("strengths", "improvements"):
            if not isinstance(generated.get(section), dict):
                raise ValueError(
                    f"Invalid {section} section in AI response."
                )

        # Keep only the requested competencies and fill missing narratives.
        for section, items in (
            ("strengths", strengths),
            ("improvements", improvements),
        ):
            for item in items:
                name = item["competency"]
                narrative = generated[section].get(name)

                if not isinstance(narrative, str) or not narrative.strip():
                    generated[section][name] = fallback[section][name]
                else:
                    generated[section][name] = narrative.strip()

        print("Bedrock narratives generated successfully.")
        return {
            "strengths": generated["strengths"],
            "improvements": generated["improvements"],
        }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
    ) as exc:
        print(f"Bedrock failed; using fallback narratives: {exc}")
        return fallback
