# src/interface/job_analysis_cli.py

"""Command-line flow for job description analysis.

Architecture position:
    interface -> engine -> storage

This module collects a pasted job description from the user, asks
whether the user wants to generate and save the analysis, calls the
engine layer, and formats the generated job analysis for terminal
display.

This module does not call Gemini directly and does not access Google
Sheets directly.

Main status contract:
    - "success": The job description was analyzed successfully.
    - "cancelled": The user chose to return to the main menu.
    - "incomplete": The job description was empty.
    - "invalid_input": The input did not appear to describe a job.
    - "ai_error": Gemini failed or returned unusable output.
    - "storage_error": The analyzed job could not be saved.
"""

from __future__ import annotations

from src.engine.job_analysis import analyze_job_description
from src.engine.job_analysis import save_existing_job_analysis
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import is_back_command
from src.interface.input_utils import print_back_instruction


def _format_list(title: str, items: list[str]) -> list[str]:
    """Format a titled list for terminal display.

    Parameters:
        title (str): Heading shown above the list.
        items (list[str]): Values to display as bullet items.

    Returns:
        list[str]: Formatted text lines. If items is empty, the returned
        list contains one fallback bullet saying "- None found".
    """

    lines = [f"{title}:"]

    if not items:
        lines.append("- None found")
        return lines

    for item in items:
        lines.append(f"- {item}")

    return lines


def format_analysis_response(response: dict) -> str:
    """Convert an engine response into readable job analysis text.

    Parameters:
        response (dict): Response payload returned by the job analysis engine.

    Returns:
        str: User-facing text for terminal display.

        Possible return values:
            If status is "success", returns formatted job analysis text with:
                - company name
                - job title
                - required skills
                - preferred skills
                - responsibilities
                - keywords
                - optional save status

            If status is not "success", returns the response message if one
            exists; otherwise, returns "Something went wrong.".
    """

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

    Parameters:
        None.

    Returns:
        str | None: Multiline text entered by the user, or None if the user
        chooses to go back to the main menu.

        Possible return values:
            str:
                All entered lines joined with newline characters. The END
                line is not included.

            None:
                The user entered a back command such as "BACK", "B", or
                "MENU".
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
    """Run the job description analysis option.

    Parameters:
        None.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "company_name": str,
                    "job_title": str,
                    "required_skills": list[str],
                    "preferred_skills": list[str],
                    "responsibilities": list[str],
                    "keywords": list[str],
                },
            }

        Success with saving:
            {
                "status": "success",
                "data": {
                    "company_name": str,
                    "job_title": str,
                    "required_skills": list[str],
                    "preferred_skills": list[str],
                    "responsibilities": list[str],
                    "keywords": list[str],
                },
                "save_status": "success" | "error",
            }

        Cancellation:
            {
                "status": "cancelled",
                "message": "Returned to main menu.",
            }

        Engine failure:
            Returns the same failure payloads as analyze_job_description(),
            including "incomplete", "invalid_input", and "ai_error".

    Side effects:
        Prints prompts and formatted output to the terminal.
    """

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

        print()
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

        print()
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