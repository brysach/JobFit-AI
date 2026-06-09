# tests/interface/test_user_profile_cli.py

from __future__ import annotations

import builtins

import src.interface.user_profile_cli as user_profile_cli


def test_split_comma_separated_items():
    result = user_profile_cli._split_comma_separated_items(
        "Python, C++, Git, , React"
    )

    assert result == ["Python", "C++", "Git", "React"]


def test_format_user_profile_response_success():
    response = {
        "status": "success",
        "save_status": "success",
        "user_id": 1,
    }

    output = user_profile_cli.format_user_profile_response(response)

    assert output == "User profile saved successfully."


def test_format_user_profile_response_error():
    response = {
        "status": "incomplete_profile",
        "message": "User profile is missing required information.",
    }

    output = user_profile_cli.format_user_profile_response(response)

    assert output == "User profile is missing required information."


def test_run_user_profile_flow(monkeypatch):
    inputs = iter(
        [
            "Bryan Estrada",
            "B.S. Computer Science, University of California, Riverside",
            "Python, C++, Git",
            "JobFit-AI",
            "Minesweeper",
            "END",
            "Math tutor",
            "Software engineering project",
            "END",
        ]
    )

    saved_profile = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_save_user_profile(user_profile: dict) -> dict:
        saved_profile.update(user_profile)
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
    assert result["user_id"] == 1

    assert "user_id" not in saved_profile
    assert saved_profile["name"] == "Bryan Estrada"
    assert saved_profile["education"] == (
        "B.S. Computer Science, University of California, Riverside"
    )
    assert saved_profile["skills"] == ["Python", "C++", "Git"]
    assert saved_profile["projects"] == ["JobFit-AI", "Minesweeper"]
    assert saved_profile["experience"] == [
        "Math tutor",
        "Software engineering project",
    ]