# src/interface/user_profile_cli.py

from __future__ import annotations

from src.engine.user_profile import save_user_profile
from src.interface.input_utils import cancelled_response
from src.interface.input_utils import input_or_back
from src.interface.input_utils import is_back_command
from src.interface.input_utils import print_back_instruction


def _split_comma_separated_items(text: str) -> list[str]:
    """Split comma-separated user input into a clean list."""

    items = []

    for item in text.split(","):
        cleaned_item = item.strip()

        if cleaned_item:
            items.append(cleaned_item)

    return items


def _read_multiline_items() -> list[str] | None:
    """Read multiline items until the user types END.

    Return None if the user chooses to go back.
    """

    items = []

    while True:
        line = input()

        if is_back_command(line):
            return None

        if line.strip().upper() == "END":
            break

        cleaned_line = line.strip()

        if cleaned_line:
            items.append(cleaned_line)

    return items


def format_user_profile_response(response: dict) -> str:
    """Format a user profile engine response for display."""

    status = response.get("status")

    if status == "success":
        return "User profile saved successfully."

    return response.get("message", "Something went wrong.")


def run_user_profile_flow() -> dict:
    """Run the user profile option."""

    print()
    print("User Profile Management")
    print("=======================")
    print_back_instruction()
    print()

    name = input_or_back("Enter your name: ")

    if name is None:
        response = cancelled_response()
        print(response["message"])
        return response

    name = name.strip()

    email = input_or_back("Enter your email: ")

    if email is None:
        response = cancelled_response()
        print(response["message"])
        return response

    email = email.strip()

    phone_number = input_or_back("Enter your phone number: ")

    if phone_number is None:
        response = cancelled_response()
        print(response["message"])
        return response

    phone_number = phone_number.strip()

    university = input_or_back("Enter your university: ")

    if university is None:
        response = cancelled_response()
        print(response["message"])
        return response

    university = university.strip()

    degree = input_or_back("Enter your degree: ")

    if degree is None:
        response = cancelled_response()
        print(response["message"])
        return response

    degree = degree.strip()

    skills_text = input_or_back("Enter your skills separated by commas: ")

    if skills_text is None:
        response = cancelled_response()
        print(response["message"])
        return response

    skills = _split_comma_separated_items(skills_text)

    print("Enter your projects, one per line.")
    print("When finished, type END on its own line.")
    projects = _read_multiline_items()

    if projects is None:
        response = cancelled_response()
        print(response["message"])
        return response

    print("Enter your work or leadership experience, one per line.")
    print("When finished, type END on its own line.")
    experience = _read_multiline_items()

    if experience is None:
        response = cancelled_response()
        print(response["message"])
        return response

    user_profile = {
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "university": university,
        "degree": degree,
        "skills": skills,
        "projects": projects,
        "experience": experience,
    }

    print()
    save_choice = input_or_back("Save this user profile? (y/n): ")

    if save_choice is None:
        response = cancelled_response()
        print(response["message"])
        return response

    if save_choice.strip().lower() != "y":
        response = {
            "status": "cancelled",
            "message": "User profile was not saved.",
        }

        print()
        print(response["message"])

        return response

    response = save_user_profile(user_profile)

    print()
    print(format_user_profile_response(response))

    return response