# src/engine/user_profile.py

from __future__ import annotations

from src.storage.user_profile_storage import get_user_profile as get_user_profile_record
from src.storage.user_profile_storage import save_user_profile as save_user_profile_record
from src.storage.user_profile_storage import delete_user_profile_by_row
from src.storage.user_profile_storage import list_user_profiles as list_user_profile_records


REQUIRED_USER_PROFILE_KEYS = {
    "name",
    "education",
    "skills",
    "projects",
    "experience",
}


def _is_non_empty_string(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_non_empty_list(value) -> bool:
    return isinstance(value, list) and len(value) > 0


def _is_valid_user_profile(user_profile: dict) -> bool:
    """Return True if the user profile has all required information."""

    if not isinstance(user_profile, dict):
        return False

    if not all(key in user_profile for key in REQUIRED_USER_PROFILE_KEYS):
        return False

    if not _is_non_empty_string(user_profile["name"]):
        return False

    if not _is_non_empty_string(user_profile["education"]):
        return False

    if not _is_non_empty_list(user_profile["skills"]):
        return False

    if not _is_non_empty_list(user_profile["projects"]):
        return False

    if not _is_non_empty_list(user_profile["experience"]):
        return False

    return True


def save_user_profile(user_profile: dict) -> dict:
    """Validate and save a user profile."""

    if not _is_valid_user_profile(user_profile):
        return {
            "status": "incomplete_profile",
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

def get_user_profile(user_id: int | str) -> dict:
    """Retrieve a user profile by user_id."""

    if user_id is None or str(user_id).strip() == "":
        return {
            "status": "incomplete_profile",
            "message": "User profile is missing required information.",
        }

    response = get_user_profile_record(user_id)

    if response.get("status") == "success":
        return response

    return {
        "status": "not_found",
        "message": "User profile was not found.",
    }

def list_user_profiles() -> dict:
    """Return all saved user profiles."""

    return list_user_profile_records()


def delete_user_profile_by_index(entry_number: int | str) -> dict:
    """Delete a saved user profile by the displayed list number."""

    try:
        selected_index = int(entry_number)
    except ValueError:
        return {
            "status": "invalid_selection",
            "message": "Please choose a valid entry number.",
        }

    response = list_user_profile_records()

    if response.get("status") != "success":
        return {
            "status": "storage_error",
            "message": "Could not retrieve user profiles.",
        }

    entries = response.get("data", [])

    if not entries:
        return {
            "status": "not_found",
            "message": "No user profiles were found.",
        }

    if selected_index < 1 or selected_index > len(entries):
        return {
            "status": "invalid_selection",
            "message": "Please choose a valid entry number.",
        }

    row_number = entries[selected_index - 1]["row_number"]
    delete_response = delete_user_profile_by_row(row_number)

    if delete_response.get("status") == "success":
        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }

    return {
        "status": "storage_error",
        "message": "Could not delete user profile.",
    }