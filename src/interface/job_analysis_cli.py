# src/interface/job_analysis_cli.py

from __future__ import annotations

from src.engine.job_analysis import analyze_job_description
from src.engine.job_analysis import save_existing_job_analysis
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import is_back_command
from src.interface.input_utils import print_back_instruction


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
        f"Company: {data.get('company_name', 'Unknown')}",
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


def _read_multiline_input() -> str | None:
    """Read multiline user input until the user types END.

    Return None if the user chooses to go back.
    """

    lines = []

    while True:
        line = input()

        if is_back_command(line):
            return None

        if line.strip().upper() == "END":
            break

        lines.append(line)

    return "\n".join(lines)


def run_job_analysis_flow() -> dict:
    """Run the job description analysis option."""

    while True:
        print()
        print("Job Description Analysis")
        print("========================")
        print_back_instruction()
        print("Paste a job description below.")
        print("When finished, type END on its own line.")
        print()

        job_description = _read_multiline_input()

        if job_description is None:
            response = cancelled_response()
            print(response["message"])
            return response

        generate_choice = input_or_back("Generate job analysis? (y/n): ")

        if generate_choice is None:
            response = cancelled_response()
            print(response["message"])
            return response

        if generate_choice.strip().lower() != "y":
            print("Job analysis was not generated. Paste a new job description.")
            continue

        response = analyze_job_description(job_description)

        print()
        print(format_analysis_response(response))

        if response.get("status") != "success":
            return response

        save_choice = input_or_back("Save this job analysis? (y/n): ")

        if save_choice is None:
            cancelled = cancelled_response()
            print(cancelled["message"])
            return cancelled

        if save_choice.strip().lower() == "y":
            save_response = save_existing_job_analysis(response["data"])

            if save_response.get("status") == "success":
                response["save_status"] = save_response["save_status"]
            else:
                response["save_status"] = "error"

            print()
            print(f"Save Status: {response['save_status']}")

        return response