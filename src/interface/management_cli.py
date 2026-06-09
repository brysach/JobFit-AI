# src/interface/management_cli.py

from __future__ import annotations

from src.engine.job_analysis import delete_job_analysis_by_index
from src.engine.job_analysis import list_job_analyses
from src.engine.user_profile import delete_user_profile_by_index
from src.engine.user_profile import list_user_profiles
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import print_back_instruction


def _format_list(title: str, items: list[str]) -> list[str]:
    lines = [f"{title}:"]

    if not items:
        lines.append("- None")
        return lines

    for item in items:
        lines.append(f"- {item}")

    return lines


def _invalid_selection_response() -> dict:
    return {
        "status": "invalid_selection",
        "message": "Please choose a valid entry number.",
    }


def _get_selected_entry(entries: list[dict], selection: str) -> dict | None:
    """Return the selected entry using the displayed list number."""

    try:
        selected_index = int(selection)
    except ValueError:
        return None

    if selected_index < 1 or selected_index > len(entries):
        return None

    return entries[selected_index - 1]


def format_user_profiles_summary_response(response: dict) -> str:
    """Format saved user profiles as a short numbered list."""

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
    """Format saved job analyses as a short numbered list."""

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
    """Format one complete user profile after it is selected."""

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
    """Format one complete job analysis after it is selected."""

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
    """Show saved users, show selected details, and delete after confirmation."""

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
    """Show saved jobs, show selected details, and delete after confirmation."""

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