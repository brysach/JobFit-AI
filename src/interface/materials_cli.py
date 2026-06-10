# src/interface/materials_cli.py

"""Command-line flow for resume and cover letter generation.

Architecture position:
    interface -> engine -> storage
    interface -> export

This module lets the user select a saved user profile and a saved job
analysis, confirms both selections, requests generated materials from
the engine layer, and optionally exports the generated content to a
.docx file.

The module handles user prompts and formatted terminal output. It does
not call Gemini directly and does not access Google Sheets directly.

Main status contract:
    - "success": Application materials were generated successfully.
    - "cancelled": The user returned to the main menu or cancelled generation.
    - "invalid_selection": The user selected an invalid list entry, or a
      selected record was missing a required backend ID.
    - "not_found": No saved user profiles or job analyses were found.
    - "incomplete_profile": The selected user profile was missing required data.
    - "missing_job_analysis": The selected job analysis was missing required data.
    - "ai_error": Gemini failed while generating materials.
    - "generation_failed": Gemini returned invalid or badly formatted output.
    - "error": The storage layer could not complete the requested operation.
"""

from __future__ import annotations

from src.engine.job_analysis import list_job_analyses
from src.engine.materials import generate_materials_for_saved_records
from src.engine.user_profile import list_user_profiles
from src.export.resume_docx import export_materials_to_docx
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import print_back_instruction
from src.interface.management_cli import format_job_analyses_summary_response
from src.interface.management_cli import format_job_analysis_details
from src.interface.management_cli import format_user_profiles_summary_response
from src.interface.management_cli import format_user_profile_details


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


def _missing_id_response(message: str) -> dict:
    """Return an invalid-selection response for a missing backend ID.

    Parameters:
        message (str): User-facing message explaining which ID is missing.

    Returns:
        dict: Invalid-selection response payload.

        Return value:
            {
                "status": "invalid_selection",
                "message": message,
            }
    """

    return {
        "status": "invalid_selection",
        "message": message,
    }


def _get_required_id(value: object) -> int | str | None:
    """Return a valid backend ID, or None if the ID is missing.

    Parameters:
        value (object): Candidate backend ID taken from a selected saved record.

    Returns:
        int | str | None: Valid ID value, or None if the value is missing.

        Possible return values:
            int:
                The ID is available as an integer.

            str:
                The ID is available as a non-empty string.

            None:
                The value is None, not an int, or an empty string.
    """

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        return value

    return None


def _get_selected_entry(entries: list[dict], selection: str) -> dict | None:
    """Return the selected entry using the displayed list number.

    Parameters:
        entries (list[dict]): Saved records displayed to the user.
        selection (str): User-entered list number.

    Returns:
        dict | None: The selected dictionary from entries, or None if the
        selection is not valid.

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


def format_materials_response(response: dict) -> str:
    """Format generated resume, cover letter, strengths, and weaknesses.

    Parameters:
        response (dict): Response payload returned by
        generate_materials_for_saved_records().

    Returns:
        str: User-facing text for terminal display.

        Possible return values:
            If status is "success", returns formatted generated materials
            with these sections:
                - resume skills
                - resume projects
                - resume experience
                - cover letter
                - strengths
                - weaknesses
                - optional save status

            If status is not "success", returns the response message if one
            exists; otherwise, returns "Something went wrong.".
    """

    status = response.get("status")

    if status != "success":
        return response.get("message", "Something went wrong.")

    data = response.get("data", {})
    resume = data.get("resume", {})

    lines = [
        "Generated Application Materials",
        "===============================",
        "",
        "Resume Preview",
        "==============",
        "",
    ]

    lines.extend(_format_list("Skills", resume.get("skills", [])))
    lines.append("")

    lines.extend(_format_list("Projects", resume.get("projects", [])))
    lines.append("")

    lines.extend(_format_list("Experience", resume.get("experience", [])))
    lines.append("")

    lines.append("Cover Letter:")
    lines.append(data.get("cover_letter", ""))

    lines.append("")
    lines.extend(_format_list("Strengths", data.get("strengths", [])))

    lines.append("")
    lines.extend(_format_list("Weaknesses", data.get("weaknesses", [])))

    if "save_status" in response:
        lines.append("")
        lines.append(f"Save Status: {response['save_status']}")

    return "\n".join(lines)


def _confirm_selected_user(selected_user: dict) -> bool | None:
    """Show selected user details and ask for confirmation.

    Parameters:
        selected_user (dict): User profile record selected from the saved
        profile list.

    Returns:
        bool | None: Confirmation result.

        Possible return values:
            True:
                The user confirmed the selected profile.

            False:
                The user did not confirm the selected profile.

            None:
                The user entered a back command and wants to return to the
                main menu.

    Side effects:
        Prints selected user profile details and reads one confirmation input
        from the terminal.
    """

    print()
    print(format_user_profile_details(selected_user))

    print()
    confirm_choice = input_or_back("Use this user profile? (y/n): ")

    if confirm_choice is None:
        return None

    return confirm_choice.strip().lower() == "y"


def _confirm_selected_job(selected_job: dict) -> bool | None:
    """Show selected job details and ask for confirmation.

    Parameters:
        selected_job (dict): Job analysis record selected from the saved job
        analysis list.

    Returns:
        bool | None: Confirmation result.

        Possible return values:
            True:
                The user confirmed the selected job analysis.

            False:
                The user did not confirm the selected job analysis.

            None:
                The user entered a back command and wants to return to the
                main menu.

    Side effects:
        Prints selected job analysis details and reads one confirmation input
        from the terminal.
    """

    print()
    print(format_job_analysis_details(selected_job))

    print()
    confirm_choice = input_or_back("Use this job analysis? (y/n): ")

    if confirm_choice is None:
        return None

    return confirm_choice.strip().lower() == "y"


def run_resume_generation_flow() -> dict:
    """Run the resume and cover letter generation option.

    Parameters:
        None.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "resume": {
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    },
                    "cover_letter": str,
                    "strengths": list[str],
                    "weaknesses": list[str],
                },
            }

        Success with saving:
            {
                "status": "success",
                "data": {
                    "resume": {
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    },
                    "cover_letter": str,
                    "strengths": list[str],
                    "weaknesses": list[str],
                },
                "save_status": "success" | "exists" | "error",
            }

        Cancellation by back command:
            {
                "status": "cancelled",
                "message": "Returned to main menu.",
            }

        Cancellation by rejecting selected profile or job:
            {
                "status": "cancelled",
                "message": "Resume generation cancelled.",
            }

        Invalid selection:
            {
                "status": "invalid_selection",
                "message": "Please choose a valid entry number.",
            }

        Missing selected user ID:
            {
                "status": "invalid_selection",
                "message": "Selected user profile is missing its user ID.",
            }

        Missing selected application ID:
            {
                "status": "invalid_selection",
                "message": "Selected job analysis is missing its application ID.",
            }

        No saved user profiles:
            {
                "status": "not_found",
                "message": "No user profiles were found.",
            }

        No saved job analyses:
            {
                "status": "not_found",
                "message": "No job analyses were found.",
            }

        Engine failure:
            Returns the same failure payloads as
            generate_materials_for_saved_records(), including
            "incomplete_profile", "missing_job_analysis", "ai_error",
            and "generation_failed".

    Side effects:
        Prints saved profile and job lists, selected record details,
        generated materials, save status, and optional .docx export status
        to the terminal.
    """

    print()
    print("Resume and Cover Letter Generation")
    print("==================================")
    print_back_instruction()

    user_profiles_response = list_user_profiles()

    print()
    print(format_user_profiles_summary_response(user_profiles_response))

    if user_profiles_response.get("status") != "success":
        return user_profiles_response

    user_profiles = user_profiles_response.get("data", [])

    if not user_profiles:
        return {
            "status": "not_found",
            "message": "No user profiles were found.",
        }

    print()
    print("Choose the user profile you want to use.")
    user_selection = input_or_back("User entry number: ")

    if user_selection is None:
        response = cancelled_response()
        print(response["message"])
        return response

    selected_user = _get_selected_entry(user_profiles, user_selection)

    if selected_user is None:
        response = _invalid_selection_response()
        print(response["message"])
        return response

    selected_user_id = _get_required_id(selected_user.get("user_id"))

    if selected_user_id is None:
        response = _missing_id_response(
            "Selected user profile is missing its user ID."
        )
        print(response["message"])
        return response

    user_confirmed = _confirm_selected_user(selected_user)

    if user_confirmed is None:
        response = cancelled_response()
        print(response["message"])
        return response

    if not user_confirmed:
        response = {
            "status": "cancelled",
            "message": "Resume generation cancelled.",
        }
        print(response["message"])
        return response

    job_analyses_response = list_job_analyses()

    print()
    print(format_job_analyses_summary_response(job_analyses_response))

    if job_analyses_response.get("status") != "success":
        return job_analyses_response

    job_analyses = job_analyses_response.get("data", [])

    if not job_analyses:
        return {
            "status": "not_found",
            "message": "No job analyses were found.",
        }

    print()
    print("Choose the job analysis you want to use.")
    job_selection = input_or_back("Job entry number: ")

    if job_selection is None:
        response = cancelled_response()
        print(response["message"])
        return response

    selected_job = _get_selected_entry(job_analyses, job_selection)

    if selected_job is None:
        response = _invalid_selection_response()
        print(response["message"])
        return response

    selected_application_id = _get_required_id(selected_job.get("application_id"))

    if selected_application_id is None:
        response = _missing_id_response(
            "Selected job analysis is missing its application ID."
        )
        print(response["message"])
        return response

    job_confirmed = _confirm_selected_job(selected_job)

    if job_confirmed is None:
        response = cancelled_response()
        print(response["message"])
        return response

    if not job_confirmed:
        response = {
            "status": "cancelled",
            "message": "Resume generation cancelled.",
        }
        print(response["message"])
        return response

    print()
    save_choice = input_or_back("Save generated materials? (y/n): ")

    if save_choice is None:
        response = cancelled_response()
        print(response["message"])
        return response

    should_save = save_choice.strip().lower() == "y"

    response = generate_materials_for_saved_records(
        user_id=selected_user_id,
        application_id=selected_application_id,
        save=should_save,
    )

    print()
    print(format_materials_response(response))

    if response.get("status") != "success":
        return response

    print()
    export_choice = input_or_back("Export generated materials to .docx? (y/n): ")

    if export_choice is None:
        print("Returned to main menu.")
        return response

    if export_choice.strip().lower() == "y":
        filename = (
            f"resume_materials_user_{selected_user_id}"
            f"_application_{selected_application_id}.docx"
        )

        try:
            file_path = export_materials_to_docx(
                materials_data=response["data"],
                user_profile=selected_user,
                filename=filename,
            )
            print(f"File saved to: {file_path}")
        except PermissionError:
            print("Could not export the .docx file because the file may already be open.")
        except Exception:
            print("Could not export the .docx file.")

    return response