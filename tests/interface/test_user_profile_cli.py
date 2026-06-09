# tests/interface/test_user_profile_cli.py

from __future__ import annotations

import builtins

import src.interface.user_profile_cli as user_profile_cli


def test_format_user_profile_response_success():
    response = {
        "status": "success",
        "save_status": "success",
    }

    output = user_profile_cli.format_user_profile_response(response)

    assert output == "User profile saved successfully."


def test_format_user_profile_response_error():
    response = {
        "status": "incomplete",
        "message": "User profile is missing required information.",
    }

    output = user_profile_cli.format_user_profile_response(response)

    assert output == "User profile is missing required information."


def test_run_user_profile_flow_success(monkeypatch):
    inputs = iter(
        [
            "Bryan Estrada",
            "bryan@example.com",
            "555-123-4567",
            "University of California, Riverside",
            "B.S. Computer Science",
            "Python, C++, Git",
            "JobFit-AI",
            "Minesweeper",
            "END",
            "Math tutor",
            "Software engineering project",
            "END",
            "y",
        ]
    )

    captured_profile = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_save_user_profile(user_profile: dict) -> dict:
        captured_profile.update(user_profile)
        return {
            "status": "success",
            "save_status": "success",
            "user_id": 1,
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        user_profile_cli,
        "save_user_profile",
        fake_save_user_profile,
    )

    result = user_profile_cli.run_user_profile_flow()

    assert result["status"] == "success"
    assert captured_profile["name"] == "Bryan Estrada"
    assert captured_profile["email"] == "bryan@example.com"
    assert captured_profile["phone_number"] == "555-123-4567"
    assert captured_profile["university"] == "University of California, Riverside"
    assert captured_profile["degree"] == "B.S. Computer Science"
    assert captured_profile["skills"] == ["Python", "C++", "Git"]
    assert captured_profile["projects"] == ["JobFit-AI", "Minesweeper"]
    assert captured_profile["experience"] == [
        "Math tutor",
        "Software engineering project",
    ]


def test_run_user_profile_flow_cancelled(monkeypatch):
    inputs = iter(
        [
            "Bryan Estrada",
            "bryan@example.com",
            "555-123-4567",
            "University of California, Riverside",
            "B.S. Computer Science",
            "Python, C++, Git",
            "JobFit-AI",
            "END",
            "Math tutor",
            "END",
            "n",
        ]
    )

    save_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_save_user_profile(user_profile: dict) -> dict:
        nonlocal save_was_called
        save_was_called = True
        return {
            "status": "success",
            "save_status": "success",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        user_profile_cli,
        "save_user_profile",
        fake_save_user_profile,
    )

    result = user_profile_cli.run_user_profile_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "User profile was not saved."
    assert save_was_called is False


def test_run_user_profile_flow_back_from_name_prompt(monkeypatch):
    inputs = iter(["BACK"])
    save_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_save_user_profile(user_profile: dict) -> dict:
        nonlocal save_was_called
        save_was_called = True
        return {
            "status": "success",
            "save_status": "success",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        user_profile_cli,
        "save_user_profile",
        fake_save_user_profile,
    )

    result = user_profile_cli.run_user_profile_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert save_was_called is False


def test_run_user_profile_flow_back_from_projects(monkeypatch):
    inputs = iter(
        [
            "Bryan Estrada",
            "bryan@example.com",
            "555-123-4567",
            "University of California, Riverside",
            "B.S. Computer Science",
            "Python, Git",
            "BACK",
        ]
    )

    save_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_save_user_profile(user_profile: dict) -> dict:
        nonlocal save_was_called
        save_was_called = True
        return {
            "status": "success",
            "save_status": "success",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        user_profile_cli,
        "save_user_profile",
        fake_save_user_profile,
    )

    result = user_profile_cli.run_user_profile_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert save_was_called is False