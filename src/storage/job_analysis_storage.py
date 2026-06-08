# src/storage/job_analysis_storage.py

from __future__ import annotations

from src.storage.google_sheets import get_worksheet


REQUIRED_JOB_ANALYSIS_KEYS = {
    "application_id",
    "job_title",
    "required_skills",
    "keywords",
}

def _comma_string_to_list(value: object) -> list[str]:
    """Convert a comma-separated string from Google Sheets into a list."""

    if value is None:
        return []

    items = []

    for item in str(value).split(","):
        cleaned_item = item.strip()

        if cleaned_item:
            items.append(cleaned_item)

    return items

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
    
def get_job_analysis(application_id: int | str) -> dict:
    """Retrieve a saved job analysis by application_id."""

    try:
        ws = get_worksheet("jobsAnalysis")
        records = ws.get_all_records()

        for record in records:
            if str(record.get("application_id")) == str(application_id):
                return {
                    "status": "success",
                    "data": {
                        "application_id": record.get("application_id"),
                        "job_title": record.get("job_title", ""),
                        "required_skills": _comma_string_to_list(
                            record.get("required_skills", "")
                        ),
                        "keywords": _comma_string_to_list(
                            record.get("keywords", "")
                        ),
                    },
                }

        return {
            "status": "not_found",
            "message": "Job analysis record was not found.",
        }
    except Exception:
        return {
            "status": "not_found",
            "message": "Job analysis record was not found.",
        }