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

Main status contract:
    - "success": The user profile was saved, listed, or deleted successfully.
    - "incomplete": The user profile is missing required information.
    - "invalid_selection": The user selected an invalid list entry.
    - "storage_error": The user profile could not be saved.
    - "not_found": No matching user profile was found.
    - "error": The storage layer could not complete the requested operation.
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
    """Return True if a value is a non-empty string.

    Parameters:
        value (object): Value to validate.

    Returns:
        bool: True if value is a string and is not empty after removing
        surrounding whitespace; otherwise, False.
    """

    return isinstance(value, str) and value.strip() != ""


def _is_valid_list(value: object) -> bool:
    """Return True if a value is a list containing only strings.

    Parameters:
        value (object): Value to validate.

    Returns:
        bool: True if value is a list and every item in the list is a
        string; otherwise, False.
    """

    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_valid_user_profile(user_profile: dict) -> bool:
    """Validate that a user profile contains all required fields.

    Parameters:
        user_profile (dict): User profile data collected by the interface
        layer.

        Expected format:
            {
                "name": str,
                "email": str,
                "phone_number": str,
                "university": str,
                "degree": str,
                "skills": list[str],
                "projects": list[str],
                "experience": list[str],
            }

    Returns:
        bool: True if the user profile contains all required keys and all
        values have the expected types; otherwise, False.
    """

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
    """Validate and save a user profile.

    Parameters:
        user_profile (dict): User profile data collected by the interface
        layer.

        Expected format:
            {
                "name": str,
                "email": str,
                "phone_number": str,
                "university": str,
                "degree": str,
                "skills": list[str],
                "projects": list[str],
                "experience": list[str],
            }

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "save_status": "success",
                "user_id": int,
            }

        Failure:
            {
                "status": "incomplete",
                "message": "User profile is missing required information.",
            }

            {
                "status": "storage_error",
                "message": "Could not save user profile.",
            }
    """

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
    """Return all saved user profiles.

    Parameters:
        None.

    Returns:
        dict: Response payload returned by the storage layer.

        Success:
            {
                "status": "success",
                "data": [
                    {
                        "row_number": int,
                        "user_id": int | str,
                        "name": str,
                        "email": str,
                        "phone_number": str,
                        "university": str,
                        "degree": str,
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    }
                ],
            }

        Failure:
            {
                "status": "not_found",
                "message": "No user profiles were found.",
            }

            {
                "status": "error",
                "message": str,
            }
    """

    return list_user_profile_records()


def delete_user_profile_by_index(entry_number: int | str) -> dict:
    """Delete a user profile using the displayed list number.

    Parameters:
        entry_number (int | str): The list number displayed to the user
        in the interface layer.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "message": "User profile deleted successfully.",
            }

        Failure:
            {
                "status": "invalid_selection",
                "message": "Please choose a valid entry number.",
            }

            {
                "status": "not_found",
                "message": "No user profiles were found.",
            }

            {
                "status": "error",
                "message": str,
            }
    """

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