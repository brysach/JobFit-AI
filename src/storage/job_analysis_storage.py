# src/storage/job_analysis_storage.py

from __future__ import annotations

from src.storage.google_sheets import get_worksheet


REQUIRED_JOB_ANALYSIS_KEYS = {
    "company_name",
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


def _parse_existing_id(value: object) -> int | None:
    """Convert an existing sheet ID into an int if possible."""

    text = str(value).strip().lstrip("'")

    try:
        return int(text)
    except ValueError:
        return None


def _get_next_application_id(ws) -> int:
    """Return the next application_id using max existing ID + 1."""

    existing_ids = ws.col_values(1)
    numeric_ids = []

    for existing_id in existing_ids:
        parsed_id = _parse_existing_id(existing_id)

        if parsed_id is not None:
            numeric_ids.append(parsed_id)

    if not numeric_ids:
        return 1

    return max(numeric_ids) + 1


def save_job_analysis(job_analysis: dict) -> dict:
    """Save analyzed job description data."""

    if not all(key in job_analysis for key in REQUIRED_JOB_ANALYSIS_KEYS):
        return {"status": "error"}

    try:
        ws = get_worksheet("jobsAnalysis")

        application_id = _get_next_application_id(ws)

        row = [
            application_id,
            job_analysis["company_name"],
            job_analysis["job_title"],
            ", ".join(job_analysis["required_skills"]),
            ", ".join(job_analysis["keywords"]),
        ]

        ws.append_row(row)

        return {
            "status": "success",
            "application_id": application_id,
        }
    except Exception:
        return {"status": "error"}


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
                        "company_name": record.get("company_name", "Unknown"),
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


def list_job_analyses() -> dict:
    """Return all saved job analyses with their sheet row numbers."""

    try:
        ws = get_worksheet("jobsAnalysis")
        records = ws.get_all_records()
        job_analyses = []

        for index, record in enumerate(records, start=2):
            job_analyses.append(
                {
                    "row_number": index,
                    "application_id": record.get("application_id"),
                    "company_name": record.get("company_name", "Unknown"),
                    "job_title": record.get("job_title", ""),
                    "required_skills": _comma_string_to_list(
                        record.get("required_skills", "")
                    ),
                    "keywords": _comma_string_to_list(record.get("keywords", "")),
                }
            )

        return {
            "status": "success",
            "data": job_analyses,
        }
    except Exception:
        return {
            "status": "error",
            "message": "Could not retrieve job analyses.",
        }


def delete_job_analysis_by_row(row_number: int) -> dict:
    """Delete a job analysis by its Google Sheets row number."""

    try:
        if row_number <= 1:
            return {"status": "error"}

        ws = get_worksheet("jobsAnalysis")
        ws.delete_rows(row_number)

        return {"status": "success"}
    except Exception:
        return {"status": "error"}