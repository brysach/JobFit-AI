# src/interface/materials_cli.py

from __future__ import annotations

from src.engine.materials import generate_materials_for_saved_records
from src.export.resume_docx import export_materials_to_docx
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
    print()

    user_id = input_or_back("Enter user ID: ")

    if user_id is None:
        response = cancelled_response()
        print(response["message"])
        return response

    user_id = user_id.strip()

    application_id = input_or_back("Enter application ID: ")

    if application_id is None:
        response = cancelled_response()
        print(response["message"])
        return response

    application_id = application_id.strip()

    save_choice = input_or_back("Save generated materials? (y/n): ")

    if save_choice is None:
        response = cancelled_response()
        print(response["message"])
        return response

    should_save = save_choice.strip().lower() == "y"

    response = generate_materials_for_saved_records(
        user_id=user_id,
        application_id=application_id,
        save=should_save,
    )

    print()
    print(format_materials_response(response))

    if response.get("status") != "success":
        return response

    export_choice = input_or_back("Export generated materials to .docx? (y/n): ")

    if export_choice is None:
        cancelled = cancelled_response()
        print(cancelled["message"])
        return response

    if export_choice.strip().lower() == "y":
        filename = f"resume_materials_user_{user_id}_application_{application_id}.docx"

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