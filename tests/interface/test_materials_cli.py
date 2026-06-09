# tests/interface/test_materials_cli.py

from __future__ import annotations

import builtins

import src.interface.materials_cli as materials_cli


def sample_success_response() -> dict:
    return {
        "status": "success",
        "data": {
            "resume_bullets": [
                "Built JobFit-AI using Python, Git, and layered architecture.",
                "Implemented tested storage and engine layers for structured application data.",
            ],
            "cover_letter": "Dear Hiring Manager, I am excited to apply.",
            "warnings": ["No direct React experience was found."],
        },
    }


def sample_user_profiles_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "row_number": 2,
                "user_id": 10,
                "name": "Bryan Estrada",
                "education": "B.S. Computer Science student",
                "skills": ["Python", "Git"],
                "projects": ["JobFit-AI"],
                "experience": ["Math tutor"],
            },
            {
                "row_number": 3,
                "user_id": 11,
                "name": "Sofia Martinez",
                "education": "B.S. Information Systems student",
                "skills": ["Java", "SQL"],
                "projects": ["Inventory Tracker"],
                "experience": ["Retail associate"],
            },
        ],
    }


def sample_job_analyses_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "row_number": 2,
                "application_id": 20,
                "job_title": "Software Engineering Intern",
                "required_skills": ["Python", "Git"],
                "keywords": ["Python", "teamwork"],
            },
            {
                "row_number": 3,
                "application_id": 21,
                "job_title": "Data Analyst Intern",
                "required_skills": ["SQL", "Excel"],
                "keywords": ["data", "dashboard"],
            },
        ],
    }


def test_format_materials_response_success():
    output = materials_cli.format_materials_response(sample_success_response())

    assert "Generated Application Materials" in output
    assert "Resume Bullets:" in output
    assert "- Built JobFit-AI using Python, Git, and layered architecture." in output
    assert "Cover Letter:" in output
    assert "Dear Hiring Manager" in output
    assert "Warnings:" in output
    assert "- No direct React experience was found." in output


def test_format_materials_response_with_save_status():
    response = sample_success_response()
    response["save_status"] = "success"

    output = materials_cli.format_materials_response(response)

    assert "Save Status: success" in output


def test_format_materials_response_error():
    response = {
        "status": "missing_job_analysis",
        "message": "Job analysis is required before generating materials.",
    }

    output = materials_cli.format_materials_response(response)

    assert output == "Job analysis is required before generating materials."


def test_run_resume_generation_flow(monkeypatch):
    inputs = iter(
        [
            "1",
            "2",
            "y",
            "n",
        ]
    )

    captured_call = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        captured_call["user_id"] = user_id
        captured_call["application_id"] = application_id
        captured_call["save"] = save

        response = sample_success_response()
        response["save_status"] = "success"
        return response

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert captured_call["user_id"] == 10
    assert captured_call["application_id"] == 21
    assert captured_call["save"] is True


def test_run_resume_generation_flow_back_from_user_selection(monkeypatch):
    inputs = iter(["BACK"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert generate_was_called is False


def test_run_resume_generation_flow_back_from_job_selection(monkeypatch):
    inputs = iter(["1", "BACK"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert generate_was_called is False


def test_run_resume_generation_flow_invalid_user_selection(monkeypatch):
    inputs = iter(["99"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."
    assert generate_was_called is False


def test_run_resume_generation_flow_invalid_job_selection(monkeypatch):
    inputs = iter(["1", "99"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."
    assert generate_was_called is False


def test_run_resume_generation_flow_no_user_profiles(monkeypatch):
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: {
            "status": "success",
            "data": [],
        },
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "not_found"
    assert result["message"] == "No user profiles were found."


def test_run_resume_generation_flow_no_job_analyses(monkeypatch):
    inputs = iter(["1"])

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: {
            "status": "success",
            "data": [],
        },
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "not_found"
    assert result["message"] == "No job analyses were found."