# src/storage/storage_handler.py

from __future__ import annotations

import os
import gspread

REQUIRED_JOB_ANALYSIS_KEYS = {
    "application_id",
    "job_title",
    "required_skills",
    "keywords",
}


def _get_worksheet():
    """Return Google Sheets worksheet."""
    # Authenticate using service_account.json
    gc = gspread.service_account(filename="service_account.json")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME", "JobFit-AI")
    sh = gc.open(sheet_name)
    return sh.get_worksheet(0)


def save_job_analysis(job_analysis: dict) -> str:
    """Save analyzed job description data.

    Return:
    - "success"
    - "exists"
    - "error"
    """
    # Validate required keys
    if not all(key in job_analysis for key in REQUIRED_JOB_ANALYSIS_KEYS):
        return "error"

    try:
        ws = _get_worksheet()

        # Check for duplicate application_id in the first column
        existing_ids = ws.col_values(1)
        if str(job_analysis["application_id"]) in existing_ids:
            return "exists"

        # Prepare row data
        # Lists are joined into comma-separated strings for storage
        row = [
            job_analysis["application_id"],
            job_analysis["job_title"],
            ", ".join(job_analysis["required_skills"]),
            ", ".join(job_analysis["keywords"]),
        ]

        ws.append_row(row)
        return "success"
    except Exception:
        # Catch all errors (auth, gspread, etc.) and return "error"
        return "error"
