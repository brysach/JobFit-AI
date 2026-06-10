# src/interface/cli.py

"""Main command-line interface for JobFit-AI.

Architecture position:
    user -> interface -> engine -> storage

This module displays the main menu, reads the user's menu choice, and
calls the correct interface flow. It does not call Gemini or Google
Sheets directly. Each feature flow handles its own input prompts and
returns a response dictionary.

The interface layer is responsible for terminal input, terminal output,
and user-facing formatting.
"""

from __future__ import annotations

from src.interface.job_analysis_cli import run_job_analysis_flow
from src.interface.materials_cli import run_resume_generation_flow
from src.interface.management_cli import run_manage_jobs_flow
from src.interface.management_cli import run_manage_users_flow
from src.interface.user_profile_cli import run_user_profile_flow


def print_menu() -> None:
    """Print the main JobFit-AI menu.

    Parameters:
        None.

    Returns:
        None.
    """

    print()
    print("========================================")
    print("              JobFit-AI")
    print("========================================")
    print("1. Add user information")
    print("2. Analyze job description")
    print("3. Generate resume")
    print("4. Manage users")
    print("5. Manage jobs")
    print("6. Exit")
    print()


def handle_menu_choice(choice: str) -> bool:
    """Handle one main menu choice.

    Parameters:
        choice (str): User's menu choice.

    Returns:
        bool: True if the program should continue running.
        bool: False if the program should exit.
    """

    normalized_choice = choice.strip()

    if normalized_choice == "1":
        run_user_profile_flow()
        return True

    if normalized_choice == "2":
        run_job_analysis_flow()
        return True

    if normalized_choice == "3":
        run_resume_generation_flow()
        return True

    if normalized_choice == "4":
        run_manage_users_flow()
        return True

    if normalized_choice == "5":
        run_manage_jobs_flow()
        return True

    if normalized_choice == "6":
        print("Goodbye.")
        return False

    print("Invalid option. Please choose a number from 1 to 6.")
    return True


def run_session() -> None:
    """Run the main command-line session loop.

    Parameters:
        None.

    Returns:
        None.
    """

    keep_running = True

    while keep_running:
        print_menu()
        choice = input("Choose an option: ")
        keep_running = handle_menu_choice(choice)


def main() -> None:
    """Start the JobFit-AI command-line program.

    Parameters:
        None.

    Returns:
        None.
    """

    run_session()


if __name__ == "__main__":
    main()