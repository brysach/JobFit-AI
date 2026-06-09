# src/interface/job_analysis_cli.py

from __future__ import annotations

from src.engine.job_analysis import analyze_and_optionally_save


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


def _read_multiline_input() -> str:
    """Read multiline user input until the user types END."""

    lines = []

    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    return "\n".join(lines)


def run_job_analysis_flow() -> dict:
    """Run the job description analysis option."""

    print()
    print("Job Description Analysis")
    print("========================")
    print("Paste a job description below.")
    print("When finished, type END on its own line.")
    print()

    job_description = _read_multiline_input()

    save_choice = input("Save this job analysis? (y/n): ").strip().lower()

    should_save = save_choice == "y"

    response = analyze_and_optionally_save(
        job_description,
        save=should_save,
    )

    print()
    print(format_analysis_response(response))

    return response