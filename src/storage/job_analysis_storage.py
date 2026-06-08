# src/storage/job_analysis_storage.py

from __future__ import annotations

from src.storage.google_sheets import get_worksheet


REQUIRED_JOB_ANALYSIS_KEYS = {
    "application_id",
    "job_title",
    "required_skills",
    "keywords",
}


def save_job_analysis(job_analysis: dict) -> str:
    """Save analyzed job description data.

    Return:
    - "success"
    - "exists"
    - "error"
    """

    if not all(key in job_analysis for key in REQUIRED_JOB_ANALYSIS_KEYS):
        return "error"

    try:
        ws = get_worksheet("jobsAnalysis")

        existing_ids = ws.col_values(1)
        if str(job_analysis["application_id"]) in existing_ids:
            return "exists"

        row = [
            job_analysis["application_id"],
            job_analysis["job_title"],
            ", ".join(job_analysis["required_skills"]),
            ", ".join(job_analysis["keywords"]),
        ]

        ws.append_row(row)
        return "success"
    except Exception:
        return "error"