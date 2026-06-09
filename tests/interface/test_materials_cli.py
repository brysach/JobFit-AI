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
            "1",
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
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert captured_call["user_id"] == "1"
    assert captured_call["application_id"] == "1"
    assert captured_call["save"] is True

def test_run_resume_generation_flow_back_from_user_id(monkeypatch):
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
        return {
            "status": "success",
            "data": {},
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert generate_was_called is False