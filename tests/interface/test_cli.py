# tests/interface/test_cli.py

from __future__ import annotations

import src.interface.cli as cli


def test_handle_menu_choice_user_profile(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli,
        "run_user_profile_flow",
        lambda: called.append("user_profile"),
    )

    result = cli.handle_menu_choice("1")

    assert result is True
    assert called == ["user_profile"]


def test_handle_menu_choice_job_analysis(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli,
        "run_job_analysis_flow",
        lambda: called.append("job_analysis"),
    )

    result = cli.handle_menu_choice("2")

    assert result is True
    assert called == ["job_analysis"]


def test_handle_menu_choice_resume_generation(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli,
        "run_resume_generation_flow",
        lambda: called.append("resume_generation"),
    )

    result = cli.handle_menu_choice("3")

    assert result is True
    assert called == ["resume_generation"]


def test_handle_menu_choice_exit(capsys):
    result = cli.handle_menu_choice("4")

    captured = capsys.readouterr()

    assert result is False
    assert "Goodbye." in captured.out


def test_handle_menu_choice_invalid(capsys):
    result = cli.handle_menu_choice("wrong")

    captured = capsys.readouterr()

    assert result is True
    assert "Invalid option" in captured.out