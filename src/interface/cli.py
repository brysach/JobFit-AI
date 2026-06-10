# src/interface/cli.py

"""Main command-line interface for JobFit-AI.

Architecture position:
    user -> interface -> engine -> storage
    user -> interface -> export

This module displays the main menu, reads the user's menu choice, and
calls the correct interface flow. It does not call Gemini or Google
Sheets directly. Each feature flow handles its own input prompts and
returns a response dictionary.

The interface layer is responsible for terminal input, terminal output,
and user-facing formatting.

Menu options:
    1. Add user information.
    2. Analyze job description.
    3. Generate resume.
    4. Manage users.
    5. Manage jobs.
    6. Exit.

Main return contract:
    This module mainly prints output and controls program flow. The
    handle_menu_choice() function returns True to continue the session
    and False to exit the session.
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
        None: This function only prints the menu to the terminal.
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
        choice (str): User's menu choice from the terminal.

    Returns:
        bool: Session-control value.

        Possible return values:
            True:
                The program should continue running. This happens after
                menu options 1 through 5, or after an invalid menu choice.

            False:
                The program should stop running. This happens when the user
                selects option 6.

    Side effects:
        Calls one feature flow based on the selected menu option:
            - "1" calls run_user_profile_flow().
            - "2" calls run_job_analysis_flow().
            - "3" calls run_resume_generation_flow().
            - "4" calls run_manage_users_flow().
            - "5" calls run_manage_jobs_flow().
            - "6" prints a goodbye message and exits the session.

        For invalid input, prints an invalid option message.
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
        None: This function keeps running until handle_menu_choice()
        returns False.

    Side effects:
        Repeatedly prints the main menu, reads one menu choice from the
        terminal, and dispatches the choice to handle_menu_choice().
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
        None: This function starts the main session loop.

    Side effects:
        Calls run_session().
    """

    run_session()


if __name__ == "__main__":
    main()