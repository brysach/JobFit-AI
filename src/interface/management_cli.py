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


def format_user_profiles_response(response: dict) -> str:
    """Format saved user profiles for display."""

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
        lines.append("")
        lines.append(f"{index}. {profile.get('name', 'Unknown user')}")
        lines.append(f"   Education: {profile.get('education', '')}")

        skills_lines = _format_list("   Skills", profile.get("skills", []))
        lines.extend(skills_lines)

        projects_lines = _format_list("   Projects", profile.get("projects", []))
        lines.extend(projects_lines)

        experience_lines = _format_list(
            "   Experience",
            profile.get("experience", []),
        )
        lines.extend(experience_lines)

    return "\n".join(lines)


def format_job_analyses_response(response: dict) -> str:
    """Format saved job analyses for display."""

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
        lines.append("")
        lines.append(f"{index}. {job.get('job_title', 'Unknown job')}")
        lines.append(f"   Company: {job.get('company_name', 'Unknown')}")

        skills_lines = _format_list(
            "   Required Skills",
            job.get("required_skills", []),
        )
        lines.extend(skills_lines)

        keywords_lines = _format_list("   Keywords", job.get("keywords", []))
        lines.extend(keywords_lines)

    return "\n".join(lines)


def run_manage_users_flow() -> dict:
    """Show saved users and let the user delete one by list number."""

    print()
    print_back_instruction()

    response = list_user_profiles()

    print()
    print(format_user_profiles_response(response))

    if response.get("status") != "success" or not response.get("data"):
        return response

    print()
    print("Choose the entry number you want to delete.")
    selection = input_or_back("Entry number to delete: ")

    if selection is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return cancelled

    delete_response = delete_user_profile_by_index(selection)

    print(delete_response.get("message", "Something went wrong."))

    return delete_response


def run_manage_jobs_flow() -> dict:
    """Show saved jobs and let the user delete one by list number."""

    print()
    print_back_instruction()

    response = list_job_analyses()

    print()
    print(format_job_analyses_response(response))

    if response.get("status") != "success" or not response.get("data"):
        return response

    print()
    print("Choose the entry number you want to delete.")
    selection = input_or_back("Entry number to delete: ")

    if selection is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return cancelled

    delete_response = delete_job_analysis_by_index(selection)

    print(delete_response.get("message", "Something went wrong."))

    return delete_response