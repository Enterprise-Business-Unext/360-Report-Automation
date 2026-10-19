import pandas as pd
import os
import sys
from column_mapper import (
    normalize_columns, 
    RESPONSE_ALIASES, 
    MAPPING_ALIASES,
    )

def app_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def load_responses():
    file_path = app_path(
        os.path.join("input", "responses.xlsx")
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Responses file not found: {file_path}"
        )

    # First, read the Excel file
    responses = pd.read_excel(file_path)

    # Then, normalize the column names
    responses = normalize_columns(
        responses,
        RESPONSE_ALIASES,
        required=[
            "Target Employee",
            "Reviewer Name",
            "Reviewer Type",
            "Competency",
            "Question ID",
            "Question",
            "Response",
        ],
    )

    return responses



def load_participant_mapping():
    file_path = app_path(
        os.path.join("input", "participant_mapping.xlsx")
    )


    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Participant mapping file not found: {file_path}"
        )

    mapping = pd.read_excel(file_path)

    mapping = normalize_columns(
        mapping,
        MAPPING_ALIASES,
        required=[
            "Target Employee",
            "Reviewer Name",
            "Reviewer Type",
        ],
    )

    return mapping



def load_settings():
    file_path = app_path(
        os.path.join("input", "settings.xlsx")
    )


    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Settings file not found: {file_path}"
        )

    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    settings = {}

    # Convert Setting-Value rows into a dictionary
    for _, row in df.iterrows():
        setting = str(row["Setting"]).strip()

        value = row["Value"]

        # Clean empty values
        if pd.isna(value):
            value = ""

        settings[setting] = value

    return settings


def load_participant_emails():
    file_path = app_path(
        os.path.join("input", "responses.xlsx")
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Responses file not found: {file_path}"
        )

    df = pd.read_excel(file_path)
    df = pd.read_excel(file_path)

    # Email extraction will be handled dynamically later.
    # For now, return an empty dictionary if email information
    # is not available in the input.
    if "Email" not in df.columns:
        return {}

    if "Reviewer Name" not in df.columns:
        return {}

    emails = (
        df[["Reviewer Name", "Email"]]
        .dropna()
        .drop_duplicates(subset=["Reviewer Name"])
    )

    return dict(
        zip(
            emails["Reviewer Name"],
            emails["Email"]
        )
    )