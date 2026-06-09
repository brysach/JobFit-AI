# src/interface/materials_cli.py

from __future__ import annotations

from src.engine.job_analysis import list_job_analyses
from src.engine.materials import generate_materials_for_saved_records
from src.engine.user_profile import list_user_profiles
from src.export.resume_docx import export_materials_to_docx
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import print_back_instruction
from src.interface.management_cli import format_job_analyses_response
from src.interface.management_cli import format_user_profiles_response


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


def format_materials_response(response: dict) -> str:
    """Format generated resume and cover letter materials for display."""

    status = response.get("status")

    if status != "success":
        return response.get("message", "Something went wrong.")

    data = response.get("data", {})

    lines = [
        "Generated Application Materials",
        "===============================",
        "",
    ]

    lines.extend(_format_list("Resume Bullets", data.get("resume_bullets", [])))
    lines.append("")

    lines.append("Cover Letter:")
    lines.append(data.get("cover_letter", ""))

    lines.append("")
    lines.extend(_format_list("Warnings", data.get("warnings", [])))

    if "save_status" in response:
        lines.append("")
        lines.append(f"Save Status: {response['save_status']}")

    return "\n".join(lines)


def run_resume_generation_flow() -> dict:
    """Run the resume and cover letter generation option."""

    print()
    print("Resume and Cover Letter Generation")
    print("==================================")
    print_back_instruction()

    user_profiles_response = list_user_profiles()

    print()
    print(format_user_profiles_response(user_profiles_response))

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

    job_analyses_response = list_job_analyses()

    print()
    print(format_job_analyses_response(job_analyses_response))

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

    save_choice = input_or_back("Save generated materials? (y/n): ")

    if save_choice is None:
        response = cancelled_response()
        print(response["message"])
        return response

    should_save = save_choice.strip().lower() == "y"

    response = generate_materials_for_saved_records(
        user_id=selected_user["user_id"],
        application_id=selected_job["application_id"],
        save=should_save,
    )

    print()
    print(format_materials_response(response))

    if response.get("status") != "success":
        return response

    export_choice = input_or_back("Export generated materials to .docx? (y/n): ")

    if export_choice is None:
        print("Returned to main menu.")
        return response

    if export_choice.strip().lower() == "y":
        filename = (
            f"resume_materials_user_{selected_user['user_id']}"
            f"_application_{selected_job['application_id']}.docx"
        )

        try:
            file_path = export_materials_to_docx(
                response["data"],
                filename=filename,
            )
            print(f"File saved to: {file_path}")
        except PermissionError:
            print("Could not export the .docx file because the file may already be open.")
        except Exception:
            print("Could not export the .docx file.")

    return response