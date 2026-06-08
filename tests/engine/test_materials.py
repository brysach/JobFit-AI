# tests/engine/test_materials.py

from __future__ import annotations

import json

import src.engine.materials as materials_engine


def sample_user_profile() -> dict:
    return {
        "user_id": 1,
        "name": "Bryan Estrada",
        "education": "B.S. Computer Science, University of California, Riverside",
        "skills": ["Python", "C++", "Git"],
        "projects": ["JobFit-AI", "Minesweeper"],
        "experience": ["Math tutor", "Software engineering project"],
    }


def sample_job_analysis() -> dict:
    return {
        "application_id": 1,
        "job_title": "Software Engineering Intern",
        "required_skills": ["Python", "Git"],
        "keywords": ["Python", "Git", "teamwork"],
    }


def sample_materials_response() -> str:
    return json.dumps(
        {
            "resume_bullets": [
                "Built JobFit-AI using Python, Git, and layered architecture.",
                "Implemented tested storage and engine layers for structured application data.",
            ],
            "cover_letter": "Dear Hiring Manager, I am excited to apply for the Software Engineering Intern position.",
            "warnings": ["No direct React experience was found in the user profile."],
        }
    )


def test_generate_application_materials_success(monkeypatch):
    monkeypatch.setattr(
        materials_engine,
        "call_gemini",
        lambda prompt: sample_materials_response(),
    )

    result = materials_engine.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "success"
    assert "resume_bullets" in result["data"]
    assert "cover_letter" in result["data"]
    assert "warnings" in result["data"]
    assert len(result["data"]["resume_bullets"]) == 2


def test_generate_application_materials_incomplete_profile():
    user_profile = sample_user_profile()
    user_profile["name"] = ""

    result = materials_engine.generate_application_materials(
        user_profile,
        sample_job_analysis(),
    )

    assert result["status"] == "incomplete_profile"
    assert result["message"] == "User profile is missing required information."


def test_generate_application_materials_missing_job_analysis():
    job_analysis = sample_job_analysis()
    del job_analysis["job_title"]

    result = materials_engine.generate_application_materials(
        sample_user_profile(),
        job_analysis,
    )

    assert result["status"] == "missing_job_analysis"
    assert result["message"] == "Job analysis is required before generating materials."


def test_generate_application_materials_ai_error(monkeypatch):
    def fake_call_gemini(prompt: str) -> str:
        raise RuntimeError("API failed")

    monkeypatch.setattr(
        materials_engine,
        "call_gemini",
        fake_call_gemini,
    )

    result = materials_engine.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "ai_error"
    assert result["message"] == "Could not generate application materials."


def test_bad_materials_json_returns_generation_failed(monkeypatch):
    monkeypatch.setattr(
        materials_engine,
        "call_gemini",
        lambda prompt: "This is not JSON",
    )

    result = materials_engine.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "generation_failed"
    assert result["message"] == "Generated content was empty or invalid."


def test_missing_generated_materials_fields_returns_generation_failed(monkeypatch):
    bad_response = json.dumps(
        {
            "resume_bullets": ["Built a Python project."],
        }
    )

    monkeypatch.setattr(
        materials_engine,
        "call_gemini",
        lambda prompt: bad_response,
    )

    result = materials_engine.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "generation_failed"
    assert result["message"] == "Generated content was empty or invalid."


def test_generate_materials_for_saved_records_success(monkeypatch):
    monkeypatch.setattr(
        materials_engine,
        "get_user_profile_record",
        lambda user_id: {
            "status": "success",
            "data": sample_user_profile(),
        },
    )

    monkeypatch.setattr(
        materials_engine,
        "get_job_analysis_record",
        lambda application_id: {
            "status": "success",
            "data": sample_job_analysis(),
        },
    )

    monkeypatch.setattr(
        materials_engine,
        "call_gemini",
        lambda prompt: sample_materials_response(),
    )

    result = materials_engine.generate_materials_for_saved_records(
        user_id=1,
        application_id=1,
        save=False,
    )

    assert result["status"] == "success"
    assert len(result["data"]["resume_bullets"]) == 2


def test_generate_materials_for_saved_records_missing_user_profile(monkeypatch):
    monkeypatch.setattr(
        materials_engine,
        "get_user_profile_record",
        lambda user_id: {
            "status": "not_found",
            "message": "User profile was not found.",
        },
    )

    result = materials_engine.generate_materials_for_saved_records(
        user_id=999,
        application_id=1,
        save=False,
    )

    assert result["status"] == "incomplete_profile"
    assert result["message"] == "User profile is missing required information."


def test_generate_materials_for_saved_records_missing_job_analysis(monkeypatch):
    monkeypatch.setattr(
        materials_engine,
        "get_user_profile_record",
        lambda user_id: {
            "status": "success",
            "data": sample_user_profile(),
        },
    )

    monkeypatch.setattr(
        materials_engine,
        "get_job_analysis_record",
        lambda application_id: {
            "status": "not_found",
            "message": "Job analysis record was not found.",
        },
    )

    result = materials_engine.generate_materials_for_saved_records(
        user_id=1,
        application_id=999,
        save=False,
    )

    assert result["status"] == "missing_job_analysis"
    assert result["message"] == "Job analysis is required before generating materials."


def test_generate_materials_for_saved_records_save_success(monkeypatch):
    saved_materials = {}

    def fake_save_generated_materials(materials: dict) -> str:
        saved_materials.update(materials)
        return "success"

    monkeypatch.setattr(
        materials_engine,
        "get_user_profile_record",
        lambda user_id: {
            "status": "success",
            "data": sample_user_profile(),
        },
    )

    monkeypatch.setattr(
        materials_engine,
        "get_job_analysis_record",
        lambda application_id: {
            "status": "success",
            "data": sample_job_analysis(),
        },
    )

    monkeypatch.setattr(
        materials_engine,
        "call_gemini",
        lambda prompt: sample_materials_response(),
    )

    monkeypatch.setattr(
        materials_engine,
        "save_generated_materials_record",
        fake_save_generated_materials,
    )

    result = materials_engine.generate_materials_for_saved_records(
        user_id=1,
        application_id=1,
        save=True,
    )

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert saved_materials["application_id"] == 1
    assert saved_materials["user_id"] == 1
    assert len(saved_materials["resume_bullets"]) == 2
    assert saved_materials["cover_letter"].startswith("Dear Hiring Manager")