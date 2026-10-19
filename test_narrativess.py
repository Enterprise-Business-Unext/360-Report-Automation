
import json
from ai_narratives import generate_narratives
from main import (
    get_competency_questions,
    load_input_files
)

# Load the actual input files used by the automation.
responses, participant_mapping, settings = load_input_files()

# Detect competencies and their questions dynamically.
competency_questions = get_competency_questions(responses)

# Use detected competencies for a basic AI integration test.
competencies = list(competency_questions.keys())

if len(competencies) < 2:
    raise ValueError(
        "At least two competencies are needed "
        "to test strengths and improvements."
    )

strengths = [
    {"competency": competencies[0], "score": 3.8}
]

improvements = [
    {"competency": competencies[1], "score": 2.4}
]

result = generate_narratives(
    strengths,
    improvements,
    competency_questions
)

print("\nGENERATED NARRATIVES:\n")
print(json.dumps(result, indent=2, ensure_ascii=False))
