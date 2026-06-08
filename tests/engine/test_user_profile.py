# tests/engine/test_user_profile.py

from __future__ import annotations

import src.engine.user_profile as user_profile_engine


def valid_user_profile() -> dict:
    return {
        "user_id": 1,
        "name": "Bryan Estrada",
        "education": "B.S. Computer Science, University of California, Riverside",
        "skills": ["Python", "C++", "Git"],
        "projects": ["JobFit-AI", "Minesweeper"],
        "experience": ["Math tutor", "Software engineering project"],
    }


def test_save_user_profile_success(monkeypatch):
    monkeypatch.setattr(
        user_profile_engine,
        "save_user_profile_record",
        lambda user_profile: "success",
    )

    result = user_profile_engine.save_user_profile(valid_user_profile())

    assert result["status"] == "success"
    assert result["save_status"] == "success"


def test_save_user_profile_incomplete_profile():
    user_profile = valid_user_profile()
    user_profile["name"] = ""

    result = user_profile_engine.save_user_profile(user_profile)

    assert result["status"] == "incomplete_profile"
    assert result["message"] == "User profile is missing required information."


def test_save_user_profile_exists(monkeypatch):
    monkeypatch.setattr(
        user_profile_engine,
        "save_user_profile_record",
        lambda user_profile: "exists",
    )

    result = user_profile_engine.save_user_profile(valid_user_profile())

    assert result["status"] == "exists"
    assert result["message"] == "User profile already exists."


def test_save_user_profile_storage_error(monkeypatch):
    monkeypatch.setattr(
        user_profile_engine,
        "save_user_profile_record",
        lambda user_profile: "error",
    )

    result = user_profile_engine.save_user_profile(valid_user_profile())

    assert result["status"] == "storage_error"
    assert result["message"] == "Could not save user profile."


def test_get_user_profile_success(monkeypatch):
    expected_response = {
        "status": "success",
        "data": valid_user_profile(),
    }

    monkeypatch.setattr(
        user_profile_engine,
        "get_user_profile_record",
        lambda user_id: expected_response,
    )

    result = user_profile_engine.get_user_profile(1)

    assert result["status"] == "success"
    assert result["data"]["name"] == "Bryan Estrada"


def test_get_user_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        user_profile_engine,
        "get_user_profile_record",
        lambda user_id: {
            "status": "not_found",
            "message": "User profile was not found.",
        },
    )

    result = user_profile_engine.get_user_profile(999)

    assert result["status"] == "not_found"
    assert result["message"] == "User profile was not found."