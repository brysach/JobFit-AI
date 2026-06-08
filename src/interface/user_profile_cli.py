# src/interface/user_profile_cli.py

from __future__ import annotations

from src.engine.user_profile import save_user_profile


def _split_comma_separated_items(text: str) -> list[str]:
    """Split comma-separated user input into a clean list."""

    items = []

    for item in text.split(","):
        cleaned_item = item.strip()

        if cleaned_item:
            items.append(cleaned_item)

    return items


def _read_multiline_items() -> list[str]:
    """Read multiline items until the user types END."""

    items = []

    while True:
        line = input()
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

    user_id = input("Enter user ID: ").strip()
    name = input("Enter your name: ").strip()
    education = input("Enter your education: ").strip()

    skills_text = input("Enter your skills separated by commas: ").strip()
    skills = _split_comma_separated_items(skills_text)

    print("Enter your projects, one per line.")
    print("When finished, type END on its own line.")
    projects = _read_multiline_items()

    print("Enter your work or leadership experience, one per line.")
    print("When finished, type END on its own line.")
    experience = _read_multiline_items()

    user_profile = {
        "user_id": user_id,
        "name": name,
        "education": education,
        "skills": skills,
        "projects": projects,
        "experience": experience,
    }

    response = save_user_profile(user_profile)

    print()
    print(format_user_profile_response(response))

    return response