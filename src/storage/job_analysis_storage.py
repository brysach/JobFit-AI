# src/storage/job_analysis_storage.py

"""Storage layer for saved job analyses.

Architecture position:
    engine -> storage -> Google Sheets

This module stores, retrieves, lists, and deletes job analysis records
in the jobsAnalysis worksheet. It is responsible for assigning new
application IDs and converting saved Google Sheets rows into structured
Python dictionaries.

This module should not collect terminal input, call Gemini, or format
user-facing output.

Google Sheet tab:
    jobsAnalysis

Expected worksheet columns:
    application_id | company_name | job_title | required_skills | keywords

Main status contract:
    - "success": The requested storage operation completed successfully.
    - "not_found": A requested job analysis record was not found.
    - "error": Required fields were missing or the Google Sheets operation failed.
"""

from __future__ import annotations

from src.storage.google_sheets import get_worksheet


REQUIRED_JOB_ANALYSIS_KEYS = {
    "company_name",
    "job_title",
    "required_skills",
    "keywords",
}


def _comma_string_to_list(value: object) -> list[str]:
    """Convert a comma-separated Google Sheets value into a list.

    Parameters:
        value (object): Value read from a Google Sheets cell. The value is
        usually a comma-separated string, but it may also be None or another
        object that can be converted to a string.

    Returns:
        list[str]: Cleaned list of non-empty strings.

        Possible return values:
            list[str]:
                A list containing each non-empty comma-separated item.

            []:
                Returned when value is None or when no non-empty items are
                found.
    """

    if value is None:
        return []

    items = []

    for item in str(value).split(","):
        cleaned_item = item.strip()

        if cleaned_item:
            items.append(cleaned_item)

    return items


def _parse_existing_id(value: object) -> int | None:
    """Convert an existing sheet ID into an integer if possible.

    Parameters:
        value (object): Existing ID value read from Google Sheets. The value
        may be an integer, a string, or a text-formatted sheet value with a
        leading apostrophe.

    Returns:
        int | None: Parsed integer ID, or None if the value cannot be parsed.

        Possible return values:
            int:
                The parsed numeric ID.

            None:
                The value could not be converted to an integer.
    """

    text = str(value).strip().lstrip("'")

    try:
        return int(text)
    except ValueError:
        return None


def _get_next_application_id(ws) -> int:
    """Return the next available application ID.

    Parameters:
        ws (gspread.worksheet.Worksheet): jobsAnalysis worksheet object.

    Returns:
        int: Next application ID calculated as max existing numeric ID + 1.
        If no numeric IDs exist, returns 1.
    """

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
    """Save analyzed job description data.

    Parameters:
        job_analysis (dict): Job analysis record prepared by the engine layer.

        Expected format:
            {
                "company_name": str,
                "job_title": str,
                "required_skills": list[str],
                "keywords": list[str],
            }

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "application_id": int,
            }

        Failure:
            {
                "status": "error",
            }

            The error status means required fields were missing or the Google
            Sheets append operation failed.
    """

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
    """Retrieve a saved job analysis by application ID.

    Parameters:
        application_id (int | str): Application ID of the saved job analysis
        record to retrieve.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "application_id": int | str,
                    "company_name": str,
                    "job_title": str,
                    "required_skills": list[str],
                    "keywords": list[str],
                },
            }

        Failure:
            {
                "status": "not_found",
                "message": "Job analysis record was not found.",
            }

            The not_found status is returned when no matching application ID
            exists or when the Google Sheets read operation fails.
    """

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
    """Return all saved job analyses with their sheet row numbers.

    Parameters:
        None.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": [
                    {
                        "row_number": int,
                        "application_id": int | str,
                        "company_name": str,
                        "job_title": str,
                        "required_skills": list[str],
                        "keywords": list[str],
                    }
                ],
            }

        Failure:
            {
                "status": "error",
                "message": "Could not retrieve job analyses.",
            }

        Notes:
            The row_number value is the actual Google Sheets row number.
            It is used internally for deletion and should not be treated as
            the same thing as application_id.
    """

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
    """Delete a job analysis by its Google Sheets row number.

    Parameters:
        row_number (int): Actual row number in the jobsAnalysis worksheet.
        The header row is row 1, so valid deletable records must have row
        number 2 or greater.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
            }

        Failure:
            {
                "status": "error",
            }

            The error status is returned if row_number is 1 or lower, or if
            the Google Sheets delete operation fails.
    """

    try:
        if row_number <= 1:
            return {"status": "error"}

        ws = get_worksheet("jobsAnalysis")
        ws.delete_rows(row_number)

        return {"status": "success"}
    except Exception:
        return {"status": "error"}