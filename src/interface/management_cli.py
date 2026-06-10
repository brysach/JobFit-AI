# src/interface/management_cli.py

"""Command-line flows for managing saved records.

Architecture position:
    interface -> engine -> storage

This module displays saved user profiles and saved job analyses,
shows full details for selected records, asks for deletion confirmation,
and sends delete requests to the engine layer.

The interface uses displayed list numbers instead of exposing backend
row numbers directly to the user.

Main status contract:
    - "success": The selected saved record was deleted successfully.
    - "cancelled": The user chose to return to the main menu or cancelled deletion.
    - "invalid_selection": The user selected an invalid list entry.
    - "not_found": No saved records were found.
    - "error": The storage layer could not complete the requested operation.
"""

from __future__ import annotations

from src.engine.job_analysis import delete_job_analysis_by_index
from src.engine.job_analysis import list_job_analyses
from src.engine.user_profile import delete_user_profile_by_index
from src.engine.user_profile import list_user_profiles
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import print_back_instruction


def _format_list(title: str, items: list[str]) -> list[str]:
    """Format a titled list for terminal display.

    Parameters:
        title (str): Heading shown above the list.
        items (list[str]): Values to display as bullet items.

    Returns:
        list[str]: Formatted text lines. If items is empty, the returned
        list contains one fallback bullet saying "- None".
    """

    lines = [f"{title}:"]

    if not items:
        lines.append("- None")
        return lines

    for item in items:
        lines.append(f"- {item}")

    return lines


def _invalid_selection_response() -> dict:
    """Return a standard invalid-selection response payload.

    Parameters:
        None.

    Returns:
        dict: Standard invalid-selection response.

        Return value:
            {
                "status": "invalid_selection",
                "message": "Please choose a valid entry number.",
            }
    """

    return {
        "status": "invalid_selection",
        "message": "Please choose a valid entry number.",
    }


def _get_selected_entry(entries: list[dict], selection: str) -> dict | None:
    """Return the selected entry using the displayed list number.

    Parameters:
        entries (list[dict]): Saved records displayed to the user.
        selection (str): User-entered list number.

    Returns:
        dict | None: The selected dictionary from entries, or None if the
        selection is not a valid integer within the displayed range.

        Possible return values:
            dict:
                The selected saved record.

            None:
                The selection could not be converted to an integer, or the
                selected number was outside the valid range.
    """

    try:
        selected_index = int(selection)
    except ValueError:
        return None

    if selected_index < 1 or selected_index > len(entries):
        return None

    return entries[selected_index - 1]


def format_user_profiles_summary_response(response: dict) -> str:
    """Format saved user profiles as a short numbered list.

    Parameters:
        response (dict): Response payload returned by list_user_profiles().

    Returns:
        str: User-facing text for terminal display.

        Possible return values:
            If status is "success" and profiles exist, returns a numbered
            list using this format:
                1. Name | University | Degree

            If status is "success" but the list is empty, returns:
                "No user profiles were found."

            If status is not "success", returns the response message if one
            exists; otherwise, returns "Could not retrieve user profiles.".
    """

    if response.get("status") != "success":
        return response.get("message", "Could not retrieve user profiles.")

    profiles = response.get("data", [])

    if not profiles:
        return "No user profiles were found."

    lines = [
        "Saved User Profiles",
        "===================",
    ]

    for index, profile in enumerate(profiles, start=1):
        name = profile.get("name", "Unknown user")
        university = profile.get("university", "")
        degree = profile.get("degree", "")
        lines.append(f"{index}. {name} | {university} | {degree}")

    return "\n".join(lines)


def format_job_analyses_summary_response(response: dict) -> str:
    """Format saved job analyses as a short numbered list.

    Parameters:
        response (dict): Response payload returned by list_job_analyses().

    Returns:
        str: User-facing text for terminal display.

        Possible return values:
            If status is "success" and jobs exist, returns a numbered list
            using this format:
                1. Company Name | Job Title

            If status is "success" but the list is empty, returns:
                "No job analyses were found."

            If status is not "success", returns the response message if one
            exists; otherwise, returns "Could not retrieve job analyses.".
    """

    if response.get("status") != "success":
        return response.get("message", "Could not retrieve job analyses.")

    jobs = response.get("data", [])

    if not jobs:
        return "No job analyses were found."

    lines = [
        "Saved Job Analyses",
        "==================",
    ]

    for index, job in enumerate(jobs, start=1):
        company_name = job.get("company_name", "Unknown")
        job_title = job.get("job_title", "Unknown job")
        lines.append(f"{index}. {company_name} | {job_title}")

    return "\n".join(lines)


def format_user_profile_details(profile: dict) -> str:
    """Format one complete user profile after it is selected.

    Parameters:
        profile (dict): Selected user profile record.

        Expected format:
            {
                "name": str,
                "email": str,
                "phone_number": str,
                "university": str,
                "degree": str,
                "skills": list[str],
                "projects": list[str],
                "experience": list[str],
            }

    Returns:
        str: User-facing text containing the selected profile's contact
        information, education information, skills, projects, and experience.
    """

    lines = [
        "Selected User Profile",
        "=====================",
        f"Name: {profile.get('name', 'Unknown user')}",
        f"Email: {profile.get('email', '')}",
        f"Phone: {profile.get('phone_number', '')}",
        f"University: {profile.get('university', '')}",
        f"Degree: {profile.get('degree', '')}",
        "",
    ]

    lines.extend(_format_list("Skills", profile.get("skills", [])))
    lines.append("")

    lines.extend(_format_list("Projects", profile.get("projects", [])))
    lines.append("")

    lines.extend(_format_list("Experience", profile.get("experience", [])))

    return "\n".join(lines)


def format_job_analysis_details(job: dict) -> str:
    """Format one complete job analysis after it is selected.

    Parameters:
        job (dict): Selected job analysis record.

        Expected format:
            {
                "company_name": str,
                "job_title": str,
                "required_skills": list[str],
                "keywords": list[str],
            }

    Returns:
        str: User-facing text containing the selected job's company name,
        job title, required skills, and keywords.
    """

    lines = [
        "Selected Job Analysis",
        "=====================",
        f"Company: {job.get('company_name', 'Unknown')}",
        f"Job Title: {job.get('job_title', 'Unknown job')}",
        "",
    ]

    lines.extend(_format_list("Required Skills", job.get("required_skills", [])))
    lines.append("")

    lines.extend(_format_list("Keywords", job.get("keywords", [])))

    return "\n".join(lines)


def run_manage_users_flow() -> dict:
    """Show saved users, show selected details, and delete after confirmation.

    Parameters:
        None.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "message": "User profile deleted successfully.",
            }

        Cancellation by back command:
            {
                "status": "cancelled",
                "message": "Returned to main menu.",
            }

        Cancellation by delete confirmation:
            {
                "status": "cancelled",
                "message": "Delete cancelled.",
            }

        Invalid selection:
            {
                "status": "invalid_selection",
                "message": "Please choose a valid entry number.",
            }

        No saved profiles:
            {
                "status": "not_found",
                "message": "No user profiles were found.",
            }

        Storage failure:
            {
                "status": "error",
                "message": str,
            }

    Side effects:
        Prints saved profile summaries, selected profile details, prompts,
        and delete status messages to the terminal.
    """

    print()
    print_back_instruction()

    response = list_user_profiles()

    print()
    print(format_user_profiles_summary_response(response))

    if response.get("status") != "success" or not response.get("data"):
        return response

    profiles = response.get("data", [])

    print()
    print("Choose the user profile you want to manage.")
    selection = input_or_back("User entry number: ")

    if selection is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return cancelled

    selected_profile = _get_selected_entry(profiles, selection)

    if selected_profile is None:
        invalid = _invalid_selection_response()
        print(invalid["message"])
        return invalid

    print()
    print(format_user_profile_details(selected_profile))

    print()
    confirm_delete = input_or_back("Delete this user profile? (y/n): ")

    if confirm_delete is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return cancelled

    if confirm_delete.strip().lower() != "y":
        response = {
            "status": "cancelled",
            "message": "Delete cancelled.",
        }
        print(response["message"])
        return response

    entry_index = profiles.index(selected_profile) + 1
    delete_response = delete_user_profile_by_index(entry_index)

    print(delete_response.get("message", "Something went wrong."))

    return delete_response


def run_manage_jobs_flow() -> dict:
    """Show saved jobs, show selected details, and delete after confirmation.

    Parameters:
        None.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "message": "Job analysis deleted successfully.",
            }

        Cancellation by back command:
            {
                "status": "cancelled",
                "message": "Returned to main menu.",
            }

        Cancellation by delete confirmation:
            {
                "status": "cancelled",
                "message": "Delete cancelled.",
            }

        Invalid selection:
            {
                "status": "invalid_selection",
                "message": "Please choose a valid entry number.",
            }

        No saved jobs:
            {
                "status": "not_found",
                "message": "No job analyses were found.",
            }

        Storage failure:
            {
                "status": "error",
                "message": str,
            }

    Side effects:
        Prints saved job summaries, selected job details, prompts, and delete
        status messages to the terminal.
    """

    print()
    print_back_instruction()

    response = list_job_analyses()

    print()
    print(format_job_analyses_summary_response(response))

    if response.get("status") != "success" or not response.get("data"):
        return response

    jobs = response.get("data", [])

    print()
    print("Choose the job analysis you want to manage.")
    selection = input_or_back("Job entry number: ")

    if selection is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return cancelled

    selected_job = _get_selected_entry(jobs, selection)

    if selected_job is None:
        invalid = _invalid_selection_response()
        print(invalid["message"])
        return invalid

    print()
    print(format_job_analysis_details(selected_job))

    print()
    confirm_delete = input_or_back("Delete this job analysis? (y/n): ")

    if confirm_delete is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return cancelled

    if confirm_delete.strip().lower() != "y":
        response = {
            "status": "cancelled",
            "message": "Delete cancelled.",
        }
        print(response["message"])
        return response

    entry_index = jobs.index(selected_job) + 1
    delete_response = delete_job_analysis_by_index(entry_index)

    print(delete_response.get("message", "Something went wrong."))

    return delete_response