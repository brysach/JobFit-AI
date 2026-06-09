# tests/storage/test_user_profile_storage.py

from __future__ import annotations

from src.storage.user_profile_storage import delete_user_profile_by_row
from src.storage.user_profile_storage import get_user_profile
from src.storage.user_profile_storage import list_user_profiles
from src.storage.user_profile_storage import save_user_profile


def valid_user_profile() -> dict:
    return {
        "name": "Bryan Estrada",
        "email": "bryan@example.com",
        "phone_number": "555-123-4567",
        "university": "University of California, Riverside",
        "degree": "B.S. Computer Science",
        "skills": ["Python", "Git"],
        "projects": ["JobFit-AI"],
        "experience": ["Math tutor"],
    }


def test_save_user_profile_success():
    result = save_user_profile(valid_user_profile())

    assert result["status"] == "success"
    assert result["user_id"] == 1


def test_save_user_profile_missing_required_field_error():
    user_profile = valid_user_profile()
    del user_profile["email"]

    result = save_user_profile(user_profile)

    assert result["status"] == "error"


def test_get_user_profile_success():
    save_result = save_user_profile(valid_user_profile())

    result = get_user_profile(save_result["user_id"])

    assert result["status"] == "success"
    assert result["data"]["name"] == "Bryan Estrada"
    assert result["data"]["email"] == "bryan@example.com"
    assert result["data"]["phone_number"] == "555-123-4567"
    assert result["data"]["university"] == "University of California, Riverside"
    assert result["data"]["degree"] == "B.S. Computer Science"
    assert result["data"]["skills"] == ["Python", "Git"]
    assert result["data"]["projects"] == ["JobFit-AI"]
    assert result["data"]["experience"] == ["Math tutor"]


def test_get_user_profile_not_found():
    result = get_user_profile(999)

    assert result["status"] == "not_found"
    assert result["message"] == "User profile was not found."


def test_list_user_profiles_success():
    save_user_profile(valid_user_profile())

    result = list_user_profiles()

    assert result["status"] == "success"
    assert len(result["data"]) == 1
    assert result["data"][0]["row_number"] == 2
    assert result["data"][0]["name"] == "Bryan Estrada"
    assert result["data"][0]["email"] == "bryan@example.com"


def test_delete_user_profile_by_row_success():
    save_user_profile(valid_user_profile())

    delete_result = delete_user_profile_by_row(2)
    list_result = list_user_profiles()

    assert delete_result["status"] == "success"
    assert list_result["data"] == []