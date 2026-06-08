# src/engine/user_profile.py

from __future__ import annotations

from src.storage.user_profile_storage import get_user_profile as get_user_profile_record
from src.storage.user_profile_storage import save_user_profile as save_user_profile_record


REQUIRED_USER_PROFILE_KEYS = {
    "user_id",
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

    if str(user_profile["user_id"]).strip() == "":
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

    save_status = save_user_profile_record(user_profile)

    if save_status == "success":
        return {
            "status": "success",
            "save_status": "success",
        }

    if save_status == "exists":
        return {
            "status": "exists",
            "message": "User profile already exists.",
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