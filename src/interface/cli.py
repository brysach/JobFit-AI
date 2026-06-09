# src/interface/cli.py

from __future__ import annotations

from src.interface.job_analysis_cli import run_job_analysis_flow
from src.interface.management_cli import run_manage_jobs_flow
from src.interface.management_cli import run_manage_users_flow
from src.interface.materials_cli import run_resume_generation_flow
from src.interface.user_profile_cli import run_user_profile_flow


def print_main_menu() -> None:
    """Display the main menu."""

    print()
    print("JobFit-AI Main Menu")
    print("===================")
    print("1. Add user information")
    print("2. Analyze job description")
    print("3. Generate resume")
    print("4. Manage users")
    print("5. Manage jobs")
    print("6. Exit")


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
        run_manage_users_flow()
        return True

    if choice == "5":
        run_manage_jobs_flow()
        return True

    if choice == "6":
        print("Goodbye.")
        return False

    print("Invalid option. Please choose 1, 2, 3, 4, 5, or 6.")
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