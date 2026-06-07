# src/interface/cli.py

from __future__ import annotations

from src.engine.engine import analyze_and_optionally_save

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