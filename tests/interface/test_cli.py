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


def test_handle_menu_choice_manage_users(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli,
        "run_manage_users_flow",
        lambda: called.append("manage_users"),
    )

    result = cli.handle_menu_choice("4")

    assert result is True
    assert called == ["manage_users"]


def test_handle_menu_choice_manage_jobs(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli,
        "run_manage_jobs_flow",
        lambda: called.append("manage_jobs"),
    )

    result = cli.handle_menu_choice("5")

    assert result is True
    assert called == ["manage_jobs"]


def test_handle_menu_choice_exit(capsys):
    result = cli.handle_menu_choice("6")

    captured = capsys.readouterr()

    assert result is False
    assert "Goodbye." in captured.out


def test_handle_menu_choice_invalid(capsys):
    result = cli.handle_menu_choice("wrong")

    captured = capsys.readouterr()

    assert result is True
    assert "Invalid option" in captured.out