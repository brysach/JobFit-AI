# src/engine/user_profile.py

"""Engine layer for user profile management.

Architecture position:
    interface -> engine -> storage

This module validates user profile data before it reaches the storage
layer. It supports saving, retrieving, listing, and deleting user
profiles. User profiles contain contact information, education details,
skills, projects, and experience used later for application material
generation.

This module does not collect terminal input and does not directly write
to Google Sheets. It delegates persistence work to the storage layer.
"""

from __future__ import annotations

from src.storage.user_profile_storage import delete_user_profile_by_row
from src.storage.user_profile_storage import list_user_profiles as list_user_profile_records
from src.storage.user_profile_storage import save_user_profile as save_user_profile_record


REQUIRED_USER_PROFILE_KEYS = {
    "name",
    "email",
    "phone_number",
    "university",
    "degree",
    "skills",
    "projects",
    "experience",
}


def _is_valid_string(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_valid_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_valid_user_profile(user_profile: dict) -> bool:
    if not isinstance(user_profile, dict):
        return False

    if not REQUIRED_USER_PROFILE_KEYS.issubset(user_profile.keys()):
        return False

    string_keys = {
        "name",
        "email",
        "phone_number",
        "university",
        "degree",
    }

    for key in string_keys:
        if not _is_valid_string(user_profile[key]):
            return False

    list_keys = {
        "skills",
        "projects",
        "experience",
    }

    for key in list_keys:
        if not _is_valid_list(user_profile[key]):
            return False

    return True


def save_user_profile(user_profile: dict) -> dict:
    """Validate and save a user profile."""

    if not _is_valid_user_profile(user_profile):
        return {
            "status": "incomplete",
            "message": "User profile is missing required information.",
        }

    save_response = save_user_profile_record(user_profile)

    if save_response.get("status") == "success":
        return {
            "status": "success",
            "save_status": "success",
            "user_id": save_response.get("user_id"),
        }

    return {
        "status": "storage_error",
        "message": "Could not save user profile.",
    }


def list_user_profiles() -> dict:
    """Return all saved user profiles."""

    return list_user_profile_records()


def delete_user_profile_by_index(entry_number: int | str) -> dict:
    """Delete a user profile using the displayed list number."""

    try:
        selected_index = int(entry_number)
    except ValueError:
        return {
            "status": "invalid_selection",
            "message": "Please choose a valid entry number.",
        }

    records_response = list_user_profile_records()

    if records_response.get("status") != "success":
        return records_response

    records = records_response.get("data", [])

    if selected_index < 1 or selected_index > len(records):
        return {
            "status": "invalid_selection",
            "message": "Please choose a valid entry number.",
        }

    row_number = records[selected_index - 1]["row_number"]

    return delete_user_profile_by_row(row_number)