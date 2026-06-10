# JobFit-AI

## Project Overview

JobFit-AI is a command-line assistant that helps users prepare job application materials. The system can analyze a job description, save structured job information, collect and save a user profile, and generate tailored resume content, a cover letter, strengths, and weaknesses for a selected job.

The project follows a layered architecture:

```text
interface -> engine -> storage
interface -> export
```

The interface layer handles terminal input and output. The engine layer validates data, calls Gemini, and controls application logic. The storage layer saves and retrieves data from Google Sheets. The export layer creates a formatted `.docx` file.

## Project Paths

| Path               | Description                                             |
| ------------------ | ------------------------------------------------------- |
| `src/`             | Source code directory                                   |
| `tests/`           | Test directory                                          |
| `FUNCTIONALITY.md` | Requirement specification                               |
| `CONTRACT.md`      | Design document with component contracts and data types |
| `requirements.txt` | Python dependencies                                     |
| `docs/`            | HTML docs with functions descriptions                      |

## Demo Video

Enter the link to see video -> https://youtu.be/c8A2jdn26P8

## Setup

### Prerequisites

- Python 3.10 or higher
- A Google Cloud service account with access to the target Google Sheet
- A Gemini API key
- A Google Sheet with these worksheet tabs:
  - `jobsAnalysis`
  - `usersProfile`
  - `generatedMaterials`

### Google Sheet Headers

The `jobsAnalysis` worksheet should use:

```text
application_id | company_name | job_title | required_skills | keywords
```

The `usersProfile` worksheet should use:

```text
user_id | name | email | phone_number | university | degree | skills | projects | experience
```

The `generatedMaterials` worksheet should use:

```text
application_id | user_id | resume_skills | resume_projects | resume_experience | cover_letter | strengths | weaknesses
```

### Service Account Setup

Place your Google Cloud service account credentials file in the project root (see `service_account.example.json` for reference):

```text
service_account.json
```

Make sure the Google Sheet is shared with the service account email address.

### Environment Variables

Set the Gemini API key before running the program.

On Git Bash or macOS/Linux:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

On Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

Optionally, set the Google Sheet name:

```bash
export GOOGLE_SHEET_NAME="JobFit-AI"
```

On Windows PowerShell:

```powershell
$env:GOOGLE_SHEET_NAME="JobFit-AI"
```

If `GOOGLE_SHEET_NAME` is not set, the program uses `JobFit-AI` as the default sheet name.

### Install Dependencies

From the project root, install the required packages:

```bash
pip install -r requirements.txt
```

The project requires:

```text
pytest>=8.0.0
pytest-cov>=5.0.0
gspread>=6.0.0
google-auth>=2.0.0
google-genai>=1.0.0
python-docx>=1.1.0
```

## Running the Program

From the project root, run:

```bash
python -m src.interface.cli
```
