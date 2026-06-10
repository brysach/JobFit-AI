# tests/interface/test_cli.py

from __future__ import annotations

import builtins

import src.interface.cli as cli


def test_print_menu_displays_all_options(capsys):
    cli.print_menu()

    captured = capsys.readouterr()

    assert "JobFit-AI" in captured.out
    assert "1. Add user information" in captured.out
    assert "2. Analyze job description" in captured.out
    assert "3. Generate resume" in captured.out
    assert "4. Manage users" in captured.out
    assert "5. Manage jobs" in captured.out
    assert "6. Exit" in captured.out


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


def test_run_session_exits_after_choice_6(monkeypatch, capsys):
    inputs = iter(["6"])

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)

    cli.run_session()

    captured = capsys.readouterr()

    assert "JobFit-AI" in captured.out
    assert "Goodbye." in captured.out


def test_run_session_repeats_after_invalid_choice(monkeypatch, capsys):
    inputs = iter(["wrong", "6"])

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)

    cli.run_session()

    captured = capsys.readouterr()

    assert "Invalid option" in captured.out
    assert "Goodbye." in captured.out


def test_run_session_calls_feature_flow_then_exits(monkeypatch):
    inputs = iter(["1", "6"])
    called = []

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_user_profile_flow():
        called.append("user_profile")

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(cli, "run_user_profile_flow", fake_user_profile_flow)

    cli.run_session()

    assert called == ["user_profile"]


def test_main_calls_run_session(monkeypatch):
    called = []

    def fake_run_session():
        called.append("run_session")

    monkeypatch.setattr(cli, "run_session", fake_run_session)

    cli.main()

    assert called == ["run_session"]