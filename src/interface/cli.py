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


def _read_multiline_input() -> str:
    """Read multiline user input until the user types END."""

    lines = []

    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    return "\n".join(lines)


def run_user_profile_flow() -> None:
    """Run the user profile option.

    This is a placeholder until user profile storage is implemented.
    """

    print()
    print("User Profile Management")
    print("=======================")
    print("This option will collect and save user information.")
    print("Next implementation step: connect this menu option to the engine.")


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

    return response


def run_resume_generation_flow() -> None:
    """Run the resume and cover letter generation option.

    This is a placeholder until generation is implemented.
    """

    print()
    print("Resume and Cover Letter Generation")
    print("==================================")
    print("This option will generate tailored resume bullets and a cover letter.")
    print("Next implementation step: connect this menu option to the engine.")


def print_main_menu() -> None:
    """Display the main menu."""

    print()
    print("JobFit-AI Main Menu")
    print("===================")
    print("1. Add user information")
    print("2. Analyze job description")
    print("3. Generate resume")
    print("4. Exit")


def handle_menu_choice(choice: str) -> bool:
    """Handle one menu choice.

    Return True to keep running.
    Return False to exit.
    """

    if choice == "1":
        run_user_profile_flow()
        return True

    if choice == "2":
        run_job_analysis_flow()
        return True

    if choice == "3":
        run_resume_generation_flow()
        return True

    if choice == "4":
        print("Goodbye.")
        return False

    print("Invalid option. Please choose 1, 2, 3, or 4.")
    return True


def main() -> None:
    """Run the command-line interface."""

    while True:
        print_main_menu()
        choice = input("Choose an option: ").strip()

        should_continue = handle_menu_choice(choice)

        if not should_continue:
            break


if __name__ == "__main__":
    main()