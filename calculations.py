import pandas as pd
import numpy as np
import math
import re


# ============================================================
# NAME NORMALIZATION
# ============================================================

def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()
    name = name.split("_")[0]
    name = re.sub(r"[^\w\s]", "", name)
    name = " ".join(name.split())

    # Remove spaces so small formatting differences don't matter
    name = name.replace(" ", "")

    return name


# ============================================================
# RATING CONVERSION
# ============================================================

rating_map = {
    "strongly agree": 4,
    "agree": 3,
    "disagree": 2,
    "strongly disagree": 1
}


def convert_ratings(df):
    """
    Convert survey responses from text ratings to numeric values.

    Expected column:
        Response

    Numeric responses are also preserved.
    """

    df = df.copy()

    if "Response" not in df.columns:
        raise ValueError(
            "Response column not found in responses.xlsx"
        )

    text = (
        df["Response"]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )

    mapped = text.astype(object).map(rating_map)

    # Also allow already-numeric responses
    numeric = pd.to_numeric(text, errors="coerce")

    df["Score"] = mapped.fillna(numeric).astype(float)

    return df


# ============================================================
# SEPARATE RESPONSES
# ============================================================

def separate_responses(employee_name, responses, mapping=None):
    """
    Separate responses for one employee into:

        Self
        Manager
        Peers
        Direct Reportees

    The reviewer type is read directly from responses.xlsx.

    mapping is kept as an optional argument so that the existing
    main.py structure does not immediately break.
    """

    required_columns = [
        "Target Employee",
        "Reviewer Name",
        "Reviewer Type",
        "Competency",
        "Question ID",
        "Question",
        "Response"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in responses.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in responses.xlsx: {missing_columns}"
        )

    # --------------------------------------------------------
    # Find responses belonging to this employee
    # --------------------------------------------------------

    employee_name_norm = normalize_name(employee_name)

    responses_copy = responses.copy()

    responses_copy["normalized_target"] = (
        responses_copy["Target Employee"]
        .apply(normalize_name)
    )

    employee_df = responses_copy[
        responses_copy["normalized_target"].apply(
            lambda x:
                x == employee_name_norm
                or employee_name_norm in x
                or x in employee_name_norm
        )
    ].copy()

    if employee_df.empty:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame()
        )

    # Convert ratings
    employee_df = convert_ratings(employee_df)

    # Normalize reviewer type
    employee_df["normalized_reviewer_type"] = (
        employee_df["Reviewer Type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------------
    # Self / Participant
    # --------------------------------------------------------

    participant_df = employee_df[
        employee_df["normalized_reviewer_type"].isin(
            ["self", "participant", "target employee"]
        )
    ].copy()

    # --------------------------------------------------------
    # Manager
    # --------------------------------------------------------

    manager_df = employee_df[
        employee_df["normalized_reviewer_type"] == "manager"
    ].copy()

    # --------------------------------------------------------
    # Peers
    # --------------------------------------------------------

    peer_df = employee_df[
        employee_df["normalized_reviewer_type"].isin(
            ["peer", "peers"]
        )
    ].copy()

    # --------------------------------------------------------
    # Direct Reportees
    # --------------------------------------------------------

    reportee_df = employee_df[
        employee_df["normalized_reviewer_type"].isin(
            [
                "direct reportee",
                "direct reportees",
                "reportee",
                "reportees"
            ]
        )
    ].copy()

    return (
        participant_df,
        manager_df,
        peer_df,
        reportee_df
    )


# ============================================================
# COMPETENCY SCORES
# ============================================================

def calculate_competency_scores(df):
    """
    Calculate average score for each competency.

    Competencies are detected dynamically from the data.

    Example:

        Customer Focus
        Adaptability
        Collaboration

    No competency names are hardcoded.
    """

    if df.empty:
        return {}

    if "Competency" not in df.columns:
        raise ValueError(
            "Competency column not found."
        )

    if "Score" not in df.columns:
        df = convert_ratings(df)

    scores = {}

    for competency, group in df.groupby("Competency"):

        valid_scores = group["Score"].dropna()

        if len(valid_scores) == 0:
            scores[competency] = np.nan
        else:
            scores[competency] = round(
                valid_scores.mean(),
                2
            )

    return scores


# ============================================================
# COHORT SCORES
# ============================================================

def calculate_cohort_scores(responses):
    """
    Calculate average competency scores across the
    entire cohort.

    Competencies are detected dynamically.
    """

    if responses.empty:
        return {}

    df = convert_ratings(responses)

    cohort_scores = {}

    for competency, group in df.groupby("Competency"):

        valid_scores = group["Score"].dropna()

        if len(valid_scores) > 0:
            cohort_scores[competency] = round(
                valid_scores.mean(),
                2
            )
        else:
            cohort_scores[competency] = np.nan

    return cohort_scores


# ============================================================
# AVERAGE OF MANAGER + PEER + REPORTEE
# ============================================================

def calculate_average_respondents(
    manager_scores,
    peer_scores,
    reportee_scores
):
    """
    Calculate average competency score from:

        Manager
        Peers
        Direct Reportees

    Only available respondent groups are included.
    """

    # Collect all competencies dynamically
    competencies = set()

    competencies.update(manager_scores.keys())
    competencies.update(peer_scores.keys())
    competencies.update(reportee_scores.keys())

    average_scores = {}

    for competency in competencies:

        scores = [
            manager_scores.get(competency),
            peer_scores.get(competency),
            reportee_scores.get(competency)
        ]

        valid_scores = [
            s for s in scores
            if s is not None
            and not pd.isna(s)
        ]

        if valid_scores:
            average_scores[competency] = round(
                sum(valid_scores) / len(valid_scores),
                2
            )
        else:
            average_scores[competency] = None

    return average_scores


# ============================================================
# QUESTION SCORES
# ============================================================

def get_question_scores(df):
    """
    Calculate average score for each question.

    Returns a dictionary instead of depending on
    fixed question positions.
    """

    if df.empty:
        return {}

    if "Score" not in df.columns:
        df = convert_ratings(df)

    question_scores = {}

    for question_id, group in df.groupby(
        "Question ID",
        sort=False
    ):

        valid_scores = group["Score"].dropna()

        if len(valid_scores) > 0:
            question_scores[question_id] = round(
                valid_scores.mean(),
                2
            )
        else:
            question_scores[question_id] = np.nan

    return question_scores


# ============================================================
# QUESTION → COMPETENCY STRUCTURE
# ============================================================

def get_competency_questions(responses):
    """
    Dynamically build:

        Competency
            ↓
        Question IDs

    Example:

        {
            "Customer Focus": ["Q1", "Q2"],
            "Adaptability": ["Q3", "Q4"],
            "Collaboration": ["Q5", "Q6"]
        }

    No competency or question names are hardcoded.
    """

    if responses.empty:
        return {}

    required_columns = [
        "Competency",
        "Question ID"
    ]

    for column in required_columns:
        if column not in responses.columns:
            raise ValueError(
                f"{column} column not found."
            )

    competency_questions = {}

    for competency, group in responses.groupby(
        "Competency",
        sort=False
    ):

        questions = (
            group["Question ID"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        competency_questions[competency] = questions

    return competency_questions


# ============================================================
# BLINDSPOTS
# ============================================================

def calculate_blindspots(
    participant_q,
    manager_q,
    peer_q,
    reportee_q,
    competency_questions
):
    """
    Calculate blindspot values dynamically.

    Positive value:
        Participant rated themselves higher than others.

    Negative value:
        Others rated the participant higher than
        the participant rated themselves.

    The calculation works with any number of competencies
    and any number of questions.
    """

    blindspots = {}

    for competency, question_ids in competency_questions.items():

        deltas = []

        for question_id in question_ids:

            participant_value = participant_q.get(
                question_id,
                np.nan
            )

            manager_value = manager_q.get(
                question_id,
                np.nan
            )

            peer_value = peer_q.get(
                question_id,
                np.nan
            )

            reportee_value = reportee_q.get(
                question_id,
                np.nan
            )

            # Participant score is required
            if pd.isna(participant_value):
                continue

            # Available external feedback
            others = [
                value
                for value in [
                    manager_value,
                    peer_value,
                    reportee_value
                ]
                if not pd.isna(value)
            ]

            if not others:
                continue

            others_average = sum(others) / len(others)

            delta = participant_value - others_average

            deltas.append(delta)

        if deltas:
            blindspots[competency] = round(
                sum(deltas) / len(deltas),
                2
            )
        else:
            blindspots[competency] = np.nan

    return blindspots