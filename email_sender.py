import os
import win32com.client


def send_report(
    recipient,
    participant_name,
    form_link,
    submission_date,
    program_name
):

    pdf_path = os.path.abspath(
        f"output/{participant_name}_360°_Feedback Report.pdf"
    )

    outlook = win32com.client.Dispatch("Outlook.Application")

    mail = outlook.CreateItem(0)

    mail.To = recipient
    
    mail.Subject = (
        f"Your Personalized 360° Feedback Report and Next Steps – "
        f"{program_name} ({participant_name})"
    )

    mail.Body = f"""Dear {participant_name},

We are pleased to share your personalised 360° Feedback Report, compiled based on the feedback provided by you, your manager, your peers, and your direct report(s).

As you review your report, we encourage you to reflect on the insights and use them to create a focused development plan.

Recommended Next Steps

• Spend some time reviewing the report and identify two strengths you would like to build on and two areas for improvement that you would like to focus on as part of your development.

• Have a discussion with your manager to validate your selections and gather additional feedback.

• Once your development areas are finalised, complete the Individual Development Plan (IDP) form included on the last page of the report and obtain your manager's sign-off.

IDP Form:
{form_link}

• Please submit the completed IDP by {submission_date}. This will help provide you the required support for your development.

We wish you the very best as you continue your leadership development journey.

Warm regards,

{program_name} Program Team
"""
    print("Recipient:", recipient)
    print("PDF exists:", os.path.exists(pdf_path))

    if os.path.exists(pdf_path):
        mail.Attachments.Add(pdf_path)
    else:
        print(f"❌ PDF not found: {pdf_path}")

    # Save the mail as a draft
    mail.Save()

    print(f"✅ Draft created for {participant_name}")