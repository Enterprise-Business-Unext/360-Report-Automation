
import re


def clean_header(header):
    """Make headers comparable despite spaces, case, and punctuation."""
    header = str(header).strip().lower()
    return re.sub(r"[^a-z0-9]", "", header)


RESPONSE_ALIASES = {
    "Target Employee": [
        "Target Employee", "Participant Name",
        "Employee Name", "Participant", "Employee"
    ],
    "Reviewer Name": [
        "Reviewer Name", "Evaluator Name",
        "Assessor Name", "Reviewer", "Evaluator"
    ],
    "Reviewer Type": [
        "Reviewer Type", "Evaluator Type",
        "Relationship", "Feedback Source"
    ],
    "Competency": [
        "Competency", "Competency Area",
        "Skill Area", "Category"
    ],
    "Question ID": [
        "Question ID", "Question Number", "QID"
    ],
    "Question": [
        "Question", "Question Text",
        "Assessment Question"
    ],
    "Response": [
        "Response", "Rating", "Answer",
        "Feedback Rating", "Score"
    ],
}

MAPPING_ALIASES = {
    "Target Employee": [
        "Target Employee", "Participant Name",
        "Employee Name", "Participant", "Employee"
    ],
    "Reviewer Name": [
        "Reviewer Name", "Evaluator Name",
        "Assessor Name", "Reviewer", "Evaluator"
    ],
    "Reviewer Type": [
        "Reviewer Type", "Evaluator Type",
        "Relationship", "Feedback Source"
    ],
    "Department": [
        "Department", "Business Unit", "Team"
    ],
    "Submission Status": [
        "Submission Status", "Status",
        "Response Status", "Completion Status"
    ],
}


def normalize_columns(df, aliases, required=None):
    """Rename recognized headers to the standard names used by the code."""
    df = df.copy()

    # Match each original column to its standardized name.
    lookup = {}
    for standard_name, alternatives in aliases.items():
        for alternative in alternatives:
            key = clean_header(alternative)
            if key in lookup and lookup[key] != standard_name:
                raise ValueError(
                    f"Ambiguous alias configuration: {alternative}"
                )
            lookup[key] = standard_name

    new_columns = []
    for column in df.columns:
        key = clean_header(column)
        new_columns.append(lookup.get(key, column))

    # Prevent two source columns from silently becoming one column.
    if len(new_columns) != len(set(new_columns)):
        raise ValueError(
            "Two or more Excel columns map to the same field. "
            "Please check the column headings."
        )

    df.columns = new_columns

    if required:
        missing = [name for name in required if name not in df.columns]
        if missing:
            raise ValueError(
                "Could not identify these required fields: "
                + ", ".join(missing)
                + ". Please check the Excel headings."
            )

    return df
