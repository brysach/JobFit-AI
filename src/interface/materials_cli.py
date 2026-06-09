# src/interface/materials_cli.py

from __future__ import annotations

from src.engine.materials import generate_materials_for_saved_records
from src.export.resume_docx import export_materials_to_docx


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

    user_id = input("Enter user ID: ").strip()
    application_id = input("Enter application ID: ").strip()

    save_choice = input("Save generated materials? (y/n): ").strip().lower()
    should_save = save_choice == "y"

    response = generate_materials_for_saved_records(
        user_id=user_id,
        application_id=application_id,
        save=should_save,
    )

    print()
    print(format_materials_response(response))
    if response.get("status") == "success":
        export_choice = input("Export generated materials to .docx? (y/n): ").strip().lower()

        if export_choice == "y":
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