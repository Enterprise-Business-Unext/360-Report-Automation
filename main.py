from data_loader import (
    load_responses,
    load_participant_mapping,
    load_settings,
    load_participant_emails
)

from calculations import (
    separate_responses,
    calculate_competency_scores,
    calculate_cohort_scores,
    calculate_average_respondents,
    get_question_scores,
    calculate_blindspots,
    get_competency_questions
)

from charts import (
    create_radar_chart,
    create_self_vs_average_radar
)

from module_charts import create_module_chart
from reports import create_report
from pdf_to_word import convert_pdf_to_word

import time
from email_sender import send_report
import traceback


# ============================================================
# LOAD DATA
# ============================================================

responses = load_responses()
mapping = load_participant_mapping()
settings = load_settings()
participant_emails = load_participant_emails()


# ============================================================
# IDENTIFY PARTICIPANTS
# ============================================================

participant_names = (
    responses["Target Employee"]
    .dropna()
    .drop_duplicates()
    .tolist()
)


# ============================================================
# DETECT COMPETENCIES AND QUESTIONS DYNAMICALLY
# ============================================================

competency_questions = get_competency_questions(responses)


# ============================================================
# MAP EACH COMPETENCY TO ITS ACTUAL QUESTION TEXT
# ============================================================

competency_question_texts = {}

for competency, question_ids in competency_questions.items():

    question_texts = []

    for question_id in question_ids:

        question_rows = responses[
            responses["Question ID"] == question_id
        ]

        if not question_rows.empty:

            question_text = str(
                question_rows.iloc[0]["Question"]
            ).strip()

            if question_text and question_text not in question_texts:
                question_texts.append(question_text)

    competency_question_texts[competency] = question_texts



# ============================================================
# CALCULATE COHORT SCORES
# ============================================================

cohort_scores = calculate_cohort_scores(responses)


# ============================================================
# GENERATE REPORTS
# ============================================================

total = len(participant_names)

start_time = time.time()

failed_reports = []


for i, participant_name in enumerate(
    participant_names,
    start=1
):

    try:

        participant_start = time.time()

        print(
            f"\n[{i}/{total}] "
            f"Generating report for {participant_name}..."
        )


        # ----------------------------------------------------
        # Separate responses
        # ----------------------------------------------------

        (
            participant,
            manager,
            peer,
            reportee
        ) = separate_responses(
            participant_name,
            responses,
            mapping
        )


        # ----------------------------------------------------
        # Calculate competency scores
        # ----------------------------------------------------

        participant_scores = calculate_competency_scores(
            participant
        )

        manager_scores = calculate_competency_scores(
            manager
        )

        peer_scores = calculate_competency_scores(
            peer
        )

        reportee_scores = calculate_competency_scores(
            reportee
        )


        # ----------------------------------------------------
        # Average Manager + Peer + Reportee
        # ----------------------------------------------------

        average_scores = calculate_average_respondents(
            manager_scores,
            peer_scores,
            reportee_scores
        )


        # ----------------------------------------------------
        # Question scores
        # ----------------------------------------------------

        participant_q = get_question_scores(
            participant
        )

        manager_q = get_question_scores(
            manager
        )

        peer_q = get_question_scores(
            peer
        )

        reportee_q = get_question_scores(
            reportee
        )


        # ----------------------------------------------------
        # Blindspots
        # ----------------------------------------------------

        blindspots = calculate_blindspots(
            participant_q,
            manager_q,
            peer_q,
            reportee_q,
            competency_questions
        )


        # ----------------------------------------------------
        # Create radar charts
        # ----------------------------------------------------

        create_radar_chart(
            participant_scores,
            manager_scores,
            peer_scores,
            reportee_scores,
            cohort_scores
        )


        create_self_vs_average_radar(
            participant_scores,
            average_scores
        )


        # ----------------------------------------------------
        # Create competency/question charts
        # ----------------------------------------------------

        for competency, question_ids in competency_questions.items():

            questions = []

            participant_values = []
            manager_values = []
            peer_values = []
            reportee_values = []


            for question_id in question_ids:

                # Get question text
                question_rows = responses[
                    responses["Question ID"] == question_id
                ]

                if not question_rows.empty:
                    question_text = (
                        question_rows.iloc[0]["Question"]
                    )
                else:
                    question_text = str(question_id)

                questions.append(question_text)


                # Get scores
                participant_values.append(
                    participant_q.get(
                        question_id,
                        float("nan")
                    )
                )

                manager_values.append(
                    manager_q.get(
                        question_id,
                        float("nan")
                    )
                )

                peer_values.append(
                    peer_q.get(
                        question_id,
                        float("nan")
                    )
                )

                reportee_values.append(
                    reportee_q.get(
                        question_id,
                        float("nan")
                    )
                )


            create_module_chart(
                competency,
                questions,
                participant_values,
                manager_values,
                peer_values,
                reportee_values
            )


        # ----------------------------------------------------
        # Create report
        # ----------------------------------------------------
        create_report(
            participant_name,
            participant_scores,
            manager_scores,
            peer_scores,
            reportee_scores,
            cohort_scores,
            average_scores,
            blindspots,
            settings.get("form_link", ""),
            settings.get("program_name","Program Name"),
            settings.get("program_year","Year"),
            competency_question_texts=competency_question_texts,
            submission_date=settings.get("idp_submission_date", "")
        )


        # ----------------------------------------------------
        # Convert PDF to Word
        # ----------------------------------------------------

        convert_pdf_to_word(
            participant_name
        )


        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        elapsed = time.time() - participant_start

        print(
            f"Time Taken: {elapsed:.2f} sec"
        )

        print(
            f"✅ {participant_name} completed."
        )


    except Exception:

        print(
            f"\n❌ Failed for {participant_name}"
        )

        traceback.print_exc()

        failed_reports.append(
            participant_name
        )

        continue
    

# ============================================================
# REPORT GENERATION SUMMARY
# ============================================================

report_generation_time = (
    time.time() - start_time
)


print("\n==============================")
print("REPORT GENERATION SUMMARY")
print("==============================")

print(
    f"Total Participants : {total}"
)

print(
    f"Successful Reports : "
    f"{total - len(failed_reports)}"
)

print(
    f"Failed Reports     : "
    f"{len(failed_reports)}"
)

print(
    f"Total Time         : "
    f"{report_generation_time:.2f} seconds"
)

if total > 0:
    print(
        f"Average Time/Report: "
        f"{report_generation_time / total:.2f} seconds"
    )

print("==============================")


if failed_reports:

    print(
        "\nParticipants with errors:"
    )

    for name in failed_reports:
        print("-", name)


# ============================================================
# OUTLOOK DRAFT CREATION
# ============================================================

choice = input(
    "\nDo you want to create Outlook drafts? (Y/N): "
).strip().upper()


if choice == "Y":

    email_start = time.time()

    for participant_name in participant_names:

        send_report(
            recipient=participant_emails.get(
                participant_name,
                ""
            ),
            participant_name=participant_name,
            form_link=settings.get(
                "form_link",
                ""
            ),
            submission_date=(
                settings.get("idp_submission_date", "").strftime("%d %B %Y")
                if hasattr(settings.get("idp_submission_date", ""), "strftime")
                else settings.get("idp_submission_date", "")
            ),
            program_name=settings.get(
                "program_name",
                ""
            )
        )

    email_time = time.time() - email_start

    print(
        "\n✅ Outlook drafts created."
    )

    print(
        f"Draft Creation Time : "
        f"{email_time:.2f} seconds"
    )

else:

    print(
        "\nEmail creation skipped."
    )