# src/interface/cli.py

from __future__ import annotations

from src.engine.engine import analyze_job_description
from src.storage.storage_handler import save_job_analysis


def _format_list(title: str, items: list[str]) -> list[str]:
    lines = [f"{title}:"]

    if not items:
        lines.append("- None found")
        return lines

    for item in items:
        lines.append(f"- {item}")

    return lines


def format_analysis_response(response: dict) -> str:
    """Convert an engine response into readable text for the user."""

    status = response.get("status")

    if status != "success":
        return response.get("message", "Something went wrong.")

    data = response.get("data", {})

    lines = [
        "Job Analysis",
        "============",
        f"Job Title: {data.get('job_title', 'Unknown')}",
        "",
    ]

    lines.extend(_format_list("Required Skills", data.get("required_skills", [])))
    lines.append("")

    lines.extend(_format_list("Preferred Skills", data.get("preferred_skills", [])))
    lines.append("")

    lines.extend(_format_list("Responsibilities", data.get("responsibilities", [])))
    lines.append("")

    lines.extend(_format_list("Keywords", data.get("keywords", [])))

    if "save_status" in response:
        lines.append("")
        lines.append(f"Save Status: {response['save_status']}")

    return "\n".join(lines)


def analyze_and_optionally_save(
    job_description: str,
    application_id: int | str | None = None,
    save: bool = False,
) -> dict:
    """Analyze a job description and optionally save the result."""

    response = analyze_job_description(job_description)

    if response.get("status") != "success":
        return response

    if not save:
        return response

    if application_id is None or str(application_id).strip() == "":
        return {
            "status": "missing_application_id",
            "message": "Application ID is required to save the job analysis.",
        }

    data = response["data"]

    job_analysis = {
        "application_id": application_id,
        "job_title": data["job_title"],
        "required_skills": data["required_skills"],
        "keywords": data["keywords"],
    }

    save_status = save_job_analysis(job_analysis)

    response["save_status"] = save_status

    return response


def main() -> None:
    """Run the command-line interface."""

    print("Welcome to JobFit-AI")
    print("Paste a job description below.")
    print("When finished, press END on its own line.")
    print()

    lines = []

    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    job_description = "\n".join(lines)

    save_choice = input("Save this job analysis? (y/n): ").strip().lower()

    application_id = None
    should_save = save_choice == "y"

    if should_save:
        application_id = input("Enter application ID: ").strip()

    response = analyze_and_optionally_save(
        job_description,
        application_id=application_id,
        save=should_save,
    )

    print()
    print(format_analysis_response(response))


if __name__ == "__main__":
    main()