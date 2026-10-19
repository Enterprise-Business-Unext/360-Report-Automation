# Report Automation — User Guide

## 1. Overview

Report Automation is a Windows application that generates individual 360-degree feedback reports from Excel input files. It calculates feedback scores, generates report visualizations, and can use Amazon Bedrock to create AI-generated narratives for key strengths and improvement areas.

The application is packaged as a Windows executable (`ReportAutomation.exe`). Users can launch it by double-clicking the executable without opening VS Code or manually running Python scripts.

## Building the Windows Executable

Build the application on a Windows computer. The project uses Windows-specific Outlook integration, so a build made on macOS or Linux is not a Windows executable.

### Build prerequisites

- 64-bit Windows and a compatible 64-bit Python installation.
- The project source files, `ReportAutomation.spec`, and the complete `assets` folder.
- Internet access while installing Python packages.

### Create the package

Open PowerShell in the project folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas numpy matplotlib reportlab pywin32 openpyxl requests python-dotenv PyMuPDF pdf2docx pyinstaller
python -m PyInstaller --clean --noconfirm ReportAutomation.spec
```

If PowerShell does not allow virtual-environment activation, run the commands using `.\.venv\Scripts\python.exe` instead of `python`, for example:

```powershell
.\.venv\Scripts\python.exe -m pip install pandas numpy matplotlib reportlab pywin32 openpyxl requests python-dotenv PyMuPDF pdf2docx pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm ReportAutomation.spec
```

The packaged application is created in `dist\ReportAutomation\`. This project uses PyInstaller's onedir mode: the EXE depends on supporting files and folders in that directory. Distribute the entire `dist\ReportAutomation\` folder, not only `ReportAutomation.exe`. Do not distribute `build\`; it contains temporary build artifacts.

Before sharing the package, create `dist\ReportAutomation\input\` and copy the three completed Excel workbooks into it. Create an empty `dist\ReportAutomation\output\` folder if it is not already present. Keep all PyInstaller-created files, including `_internal` or other support folders, exactly where PyInstaller placed them. The `assets` folder is included by `ReportAutomation.spec`; do not remove or move the bundled assets.

For a ZIP handoff, zip the complete `dist\ReportAutomation\` folder. Extract it on the receiving Windows computer before running the EXE. The receiving computer does not need Python installed.

### Configure Bedrock credentials

AI narratives are optional. To enable them, create a file named `.env` beside `ReportAutomation.exe`, using `.env.example` as a template:

```dotenv
AWS_BEARER_TOKEN_BEDROCK=your_approved_bedrock_token
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=apac.amazon.nova-lite-v1:0
```

Replace the placeholder with an approved credential. Never put a real token in the source repository, the shared application ZIP, or this README. Provide credentials to the person running the app through an approved secure channel. Without a valid token, reports use fallback narrative text; the rest of the report generation can still run.

### Run the packaged application

The input workbooks must be in the `input` folder beside the EXE. Run the app with its working directory set to the packaged folder so generated files go into that folder's `output` directory. In PowerShell, from the project folder:

```powershell
Set-Location .\dist\ReportAutomation
.\ReportAutomation.exe
```

The app opens a console window and prints progress. Keep it open until processing finishes. At the prompt `Do you want to create Outlook drafts? (Y/N):`, enter `Y` to create drafts or `N` to skip. Creating drafts requires Outlook for Windows to be installed and configured. Do not start another run until the current run has completed.

The generated Word/PDF reports and charts are written under `output\`. Review the final success and failure summary and inspect the reports before sharing them.

## 2. System Requirements

- Windows laptop or desktop.
- The complete extracted application folder.
- Excel input files prepared using the supplied templates.
- Approved Amazon Bedrock credentials and access, if AI-generated narratives are required.
- Permission to read and write files in the application folder.

## 3. Application Folder Structure

The PyInstaller support-file layout can vary by PyInstaller version. Keep the complete extracted folder together. At minimum, the application folder should contain the executable, the input workbooks, and an output folder:

```text
ReportAutomation/
├── ReportAutomation.exe
├── _internal/                 # May contain bundled runtime files
├── input/
│   ├── responses.xlsx
│   ├── participant_mapping.xlsx
│   └── settings.xlsx
└── output/
```

There may be additional PyInstaller support files or folders. The bundled assets may be inside a support folder rather than beside the EXE; keep the generated package unchanged. The optional `.env` file belongs beside `ReportAutomation.exe`.

**Important:** Keep the executable and all its supporting folders together. Do not move the EXE or delete bundled files.

- **ReportAutomation.exe:** Starts the report-generation process.
- **Bundled assets:** Contains report design files, images, and other resources.
- **input:** Contains the Excel files used by the application.
- **output:** Stores generated reports and supporting charts.

If the `output` folder is missing, create a folder named `output` beside the executable and start the application with that folder as its working directory.

## 4. Preparing the Input Files

Three Excel files are required. Keep their filenames unchanged.

### 4.1 responses.xlsx

This file contains survey responses. Use the supplied template and ensure that the required columns are present:

| Column | Description |
|---|---|
| Target Employee | Person whose report will be generated |
| Reviewer Name | Person providing the feedback |
| Reviewer Type | Self, manager, peer, direct reportee, etc. |
| Competency | Competency being assessed |
| Question ID | Identifier for the question, e.g. Q01 |
| Question | Full assessment question |
| Response | Rating submitted by the reviewer |

Each row should represent one answer to one question by one reviewer for one target employee.

Do not paste multiple responses into a single cell. Make sure names, question IDs, competency names, and ratings are consistent.

### 4.2 participant_mapping.xlsx

This file maps target employees to their reviewers.

Use the supplied template and retain the columns included in it, such as:

- Target Employee
- Reviewer Name
- Reviewer Type
- Department
- Submission Status

Ensure that employee and reviewer names match the corresponding names in `responses.xlsx`.

### 4.3 settings.xlsx

This file contains report configuration. Preserve the template's `Setting` and `Value` structure.

Settings in the current setup include:

- Report Title
- program_name
- program_year
- Rating Scale
- Strongly Agree Score
- Agree Score
- Disagree Score
- Strongly Disagree Score

The current rating example is:

- Strongly Agree = 4
- Agree = 3
- Disagree = 2
- Strongly Disagree = 1

Use the rating scale agreed for the relevant program. Do not change scoring values unless the questionnaire uses a different approved scale.

## 5. Configuring AI Narratives

The application uses Amazon Bedrock to generate narratives for strengths and improvement areas.

The expected environment-variable name is:

`AWS_BEARER_TOKEN_BEDROCK`

The current model configuration uses:

- Region: `ap-south-1`
- Model: `apac.amazon.nova-lite-v1:0`

AI-generated narratives require valid credentials, network access, and the appropriate Bedrock permissions.

If the application reports that the Bedrock key is missing or the request fails, it may use generic fallback descriptions instead. The report may still be generated, but the narratives will not be AI-generated.

**Credential security:**

- Use only credentials approved by the organization.
- Never include a real API key in the shared ZIP, source code, README, screenshots, or email.
- Do not distribute your personal `.env` file.
- If the application is configured to load a local `.env` file, follow the application owner's instructions for setting up credentials on the machine where it will run.
- Contact IT or the application owner if Bedrock access is unavailable.

## 6. How to Run the Application

Follow these steps for each batch.

1. Copy the application ZIP to the Windows computer.
2. Right-click the ZIP and select **Extract All**.
3. Open the extracted application folder.
4. Open the `input` folder.
5. Place the three completed Excel files inside it:
   - `responses.xlsx`
   - `participant_mapping.xlsx`
   - `settings.xlsx`
6. Keep all PyInstaller-created support files and folders in place; the bundled assets do not need to be beside the executable.
7. Create a `.env` file beside the executable with approved Bedrock credentials if AI narratives are required.
8. Open PowerShell in the main application folder and start `ReportAutomation.exe` from there. This ensures output files are written to that folder's `output` directory.
9. A terminal window will display the report-generation progress.
10. Keep the window open until processing and the summary are complete.
11. If prompted:

    `Do you want to create Outlook drafts? (Y/N):`

    - Enter `Y` to attempt the configured Outlook draft workflow.
    - Enter `N` to skip draft creation.
12. Wait for the application to finish before closing the terminal.

Do not launch the executable multiple times while a batch is running.

## 7. Where to Find the Reports

Open the `output` folder beside the executable.

Generated Word reports have filenames similar to:

`Participant Name_360°_Feedback Report.docx`

The application may also generate PDF reports and supporting chart files.

After processing, check the terminal summary for:

- Total participants
- Successful reports
- Failed reports
- Total processing time

Verify that the expected reports exist in the output folder. Review any failed participants before considering the batch complete.

Before distributing reports, check the participant name, program details, scores, charts, strengths, improvement areas, blind spots, and AI narratives.

## 8. Troubleshooting

### The application does not start

- Extract the complete ZIP before running the executable.
- Keep the EXE and supporting folders together.
- Follow organizational software-security procedures if Windows displays a warning.

### An input file is missing

- Check that the `input` folder is beside the executable.
- Confirm that all three filenames are correct.
- Ensure the files are not open or locked by another application.

### Input or column errors occur

- Start with the supplied templates.
- Confirm that required columns are present.
- Check for blank names, inconsistent spellings, invalid ratings, or incorrectly formatted rows.
- Ensure that each survey response occupies its own row.

### AI narratives are generic

- Check the terminal for Bedrock credential or request errors.
- Confirm that approved credentials are configured and accessible to the application.
- Ask IT to verify network access and Bedrock permissions.
- Never share the API key when reporting an issue.

### A participant's report fails

- Read the terminal error associated with that participant.
- Check the participant's data for missing reviewer responses or inconsistent names.
- Close any existing PDF or Word report with the same filename before retrying.
- Record the error and contact the application owner if it continues.

### Outlook drafts are not created

- Choose `N` if draft creation is not required.
- If drafts are required, verify that Outlook is configured and signed in and that the workflow is permitted by organizational policy.

## 9. Best Practices

- Keep an untouched copy of the original input files.
- Back up existing reports before rerunning a batch.
- Do not modify or delete files inside `assets`.
- Do not share `.env` files, API keys, or passwords.
- Treat participant feedback and reports as confidential information.
- Share reports only through approved company channels.
- Check both successful and failed report counts before confirming completion.
