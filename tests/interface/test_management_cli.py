# tests/interface/test_management_cli.py

from __future__ import annotations

import builtins

import src.interface.management_cli as management_cli


def sample_user_profiles_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "row_number": 2,
                "user_id": 1,
                "name": "Bryan Estrada",
                "education": "B.S. Computer Science student",
                "skills": ["Python", "Git"],
                "projects": ["JobFit-AI"],
                "experience": ["Math tutor"],
            }
        ],
    }


def sample_job_analyses_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "row_number": 2,
                "application_id": 1,
                "company_name": "TechStart",
                "job_title": "Software Engineering Intern",
                "required_skills": ["Python", "Git"],
                "keywords": ["Python", "teamwork"],
            }
        ],
    }


def test_format_user_profiles_summary_response_success():
    output = management_cli.format_user_profiles_summary_response(
        sample_user_profiles_response()
    )

    assert "Saved User Profiles" in output
    assert "1. Bryan Estrada | B.S. Computer Science student" in output
    assert "- Python" not in output
    assert "- JobFit-AI" not in output


def test_format_user_profiles_summary_response_empty():
    response = {
        "status": "success",
        "data": [],
    }

    output = management_cli.format_user_profiles_summary_response(response)

    assert output == "No user profiles were found."


def test_format_user_profile_details():
    profile = sample_user_profiles_response()["data"][0]

    output = management_cli.format_user_profile_details(profile)

    assert "Selected User Profile" in output
    assert "Name: Bryan Estrada" in output
    assert "Education: B.S. Computer Science student" in output
    assert "- Python" in output
    assert "- Git" in output
    assert "- JobFit-AI" in output
    assert "- Math tutor" in output


def test_format_job_analyses_summary_response_success():
    output = management_cli.format_job_analyses_summary_response(
        sample_job_analyses_response()
    )

    assert "Saved Job Analyses" in output
    assert "1. TechStart | Software Engineering Intern" in output
    assert "- Python" not in output
    assert "- teamwork" not in output


def test_format_job_analyses_summary_response_empty():
    response = {
        "status": "success",
        "data": [],
    }

    output = management_cli.format_job_analyses_summary_response(response)

    assert output == "No job analyses were found."


def test_format_job_analysis_details():
    job = sample_job_analyses_response()["data"][0]

    output = management_cli.format_job_analysis_details(job)

    assert "Selected Job Analysis" in output
    assert "Company: TechStart" in output
    assert "Job Title: Software Engineering Intern" in output
    assert "- Python" in output
    assert "- Git" in output
    assert "- teamwork" in output


def test_run_manage_users_flow_delete_success(monkeypatch):
    inputs = iter(["1", "y"])
    captured_selection = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_user_profile_by_index(selection: int | str) -> dict:
        captured_selection["selection"] = selection
        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_user_profile_by_index",
        fake_delete_user_profile_by_index,
    )

    result = management_cli.run_manage_users_flow()

    assert result["status"] == "success"
    assert captured_selection["selection"] == 1


def test_run_manage_users_flow_delete_not_confirmed(monkeypatch):
    inputs = iter(["1", "n"])
    delete_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_user_profile_by_index(selection: int | str) -> dict:
        nonlocal delete_was_called
        delete_was_called = True
        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_user_profile_by_index",
        fake_delete_user_profile_by_index,
    )

    result = management_cli.run_manage_users_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Delete cancelled."
    assert delete_was_called is False


def test_run_manage_users_flow_back_from_selection(monkeypatch):
    inputs = iter(["BACK"])
    delete_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_user_profile_by_index(selection: int | str) -> dict:
        nonlocal delete_was_called
        delete_was_called = True
        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_user_profile_by_index",
        fake_delete_user_profile_by_index,
    )

    result = management_cli.run_manage_users_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert delete_was_called is False


def test_run_manage_users_flow_invalid_selection(monkeypatch):
    inputs = iter(["99"])
    delete_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_user_profile_by_index(selection: int | str) -> dict:
        nonlocal delete_was_called
        delete_was_called = True
        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_user_profile_by_index",
        fake_delete_user_profile_by_index,
    )

    result = management_cli.run_manage_users_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."
    assert delete_was_called is False


def test_run_manage_jobs_flow_delete_success(monkeypatch):
    inputs = iter(["1", "y"])
    captured_selection = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_job_analysis_by_index(selection: int | str) -> dict:
        captured_selection["selection"] = selection
        return {
            "status": "success",
            "message": "Job analysis deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_job_analysis_by_index",
        fake_delete_job_analysis_by_index,
    )

    result = management_cli.run_manage_jobs_flow()

    assert result["status"] == "success"
    assert captured_selection["selection"] == 1


def test_run_manage_jobs_flow_delete_not_confirmed(monkeypatch):
    inputs = iter(["1", "n"])
    delete_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_job_analysis_by_index(selection: int | str) -> dict:
        nonlocal delete_was_called
        delete_was_called = True
        return {
            "status": "success",
            "message": "Job analysis deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_job_analysis_by_index",
        fake_delete_job_analysis_by_index,
    )

    result = management_cli.run_manage_jobs_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Delete cancelled."
    assert delete_was_called is False


def test_run_manage_jobs_flow_back_from_selection(monkeypatch):
    inputs = iter(["BACK"])
    delete_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_job_analysis_by_index(selection: int | str) -> dict:
        nonlocal delete_was_called
        delete_was_called = True
        return {
            "status": "success",
            "message": "Job analysis deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_job_analysis_by_index",
        fake_delete_job_analysis_by_index,
    )

    result = management_cli.run_manage_jobs_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert delete_was_called is False


def test_run_manage_jobs_flow_invalid_selection(monkeypatch):
    inputs = iter(["99"])
    delete_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_delete_job_analysis_by_index(selection: int | str) -> dict:
        nonlocal delete_was_called
        delete_was_called = True
        return {
            "status": "success",
            "message": "Job analysis deleted successfully.",
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        management_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        management_cli,
        "delete_job_analysis_by_index",
        fake_delete_job_analysis_by_index,
    )

    result = management_cli.run_manage_jobs_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."
    assert delete_was_called is False