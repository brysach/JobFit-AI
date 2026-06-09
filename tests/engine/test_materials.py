# tests/engine/test_materials.py

from __future__ import annotations

import json

import src.engine.materials as materials


def sample_user_profile() -> dict:
    return {
        "user_id": 1,
        "name": "Bryan Estrada",
        "email": "bryan@example.com",
        "phone_number": "555-123-4567",
        "university": "University of California, Riverside",
        "degree": "B.S. Computer Science",
        "skills": ["Python", "Git"],
        "projects": ["JobFit-AI"],
        "experience": ["Math tutor"],
    }


def sample_job_analysis() -> dict:
    return {
        "application_id": 1,
        "company_name": "TechStart",
        "job_title": "Software Engineering Intern",
        "required_skills": ["Python", "Git"],
        "keywords": ["Python", "teamwork"],
    }


def sample_gemini_response() -> str:
    return json.dumps(
        {
            "resume": {
                "skills": ["Python", "Git"],
                "projects": ["Built JobFit-AI using Python and layered architecture."],
                "experience": ["Tutored students in problem-solving and communication."],
            },
            "cover_letter": "Dear TechStart Hiring Team, I am excited to apply.",
            "strengths": [
                "Your Python and Git experience matches core requirements for this role."
            ],
            "weaknesses": [
                "Review common software engineering intern assessment problems before interviewing."
            ],
        }
    )


def test_generate_application_materials_success(monkeypatch):
    monkeypatch.setattr(
        materials,
        "call_gemini",
        lambda prompt: sample_gemini_response(),
    )

    result = materials.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "success"
    assert result["data"]["resume"]["skills"] == ["Python", "Git"]
    assert result["data"]["resume"]["projects"] == [
        "Built JobFit-AI using Python and layered architecture."
    ]
    assert result["data"]["resume"]["experience"] == [
        "Tutored students in problem-solving and communication."
    ]
    assert "TechStart" in result["data"]["cover_letter"]
    assert result["data"]["strengths"] == [
        "Your Python and Git experience matches core requirements for this role."
    ]
    assert result["data"]["weaknesses"] == [
        "Review common software engineering intern assessment problems before interviewing."
    ]


def test_generate_application_materials_incomplete_profile():
    profile = sample_user_profile()
    del profile["email"]

    result = materials.generate_application_materials(
        profile,
        sample_job_analysis(),
    )

    assert result["status"] == "incomplete_profile"


def test_generate_application_materials_missing_job_analysis():
    job_analysis = sample_job_analysis()
    del job_analysis["company_name"]

    result = materials.generate_application_materials(
        sample_user_profile(),
        job_analysis,
    )

    assert result["status"] == "missing_job_analysis"


def test_generate_application_materials_ai_error(monkeypatch):
    def fake_call_gemini(prompt: str) -> str:
        raise RuntimeError("API error")

    monkeypatch.setattr(materials, "call_gemini", fake_call_gemini)

    result = materials.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "ai_error"
    assert result["message"] == "Could not generate application materials."


def test_generate_application_materials_generation_failed(monkeypatch):
    monkeypatch.setattr(
        materials,
        "call_gemini",
        lambda prompt: "not json",
    )

    result = materials.generate_application_materials(
        sample_user_profile(),
        sample_job_analysis(),
    )

    assert result["status"] == "generation_failed"


def test_generate_materials_for_saved_records_success(monkeypatch):
    captured_save = {}

    monkeypatch.setattr(
        materials,
        "get_user_profile",
        lambda user_id: {
            "status": "success",
            "data": sample_user_profile(),
        },
    )
    monkeypatch.setattr(
        materials,
        "get_job_analysis",
        lambda application_id: {
            "status": "success",
            "data": sample_job_analysis(),
        },
    )
    monkeypatch.setattr(
        materials,
        "call_gemini",
        lambda prompt: sample_gemini_response(),
    )

    def fake_save_generated_materials_record(record: dict) -> str:
        captured_save.update(record)
        return "success"

    monkeypatch.setattr(
        materials,
        "save_generated_materials_record",
        fake_save_generated_materials_record,
    )

    result = materials.generate_materials_for_saved_records(
        user_id=1,
        application_id=1,
        save=True,
    )

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert captured_save["application_id"] == 1
    assert captured_save["user_id"] == 1
    assert captured_save["resume_skills"] == ["Python", "Git"]
    assert captured_save["resume_projects"] == [
        "Built JobFit-AI using Python and layered architecture."
    ]
    assert captured_save["resume_experience"] == [
        "Tutored students in problem-solving and communication."
    ]
    assert captured_save["strengths"] == [
        "Your Python and Git experience matches core requirements for this role."
    ]
    assert captured_save["weaknesses"] == [
        "Review common software engineering intern assessment problems before interviewing."
    ]


def test_generate_materials_for_saved_records_user_not_found(monkeypatch):
    monkeypatch.setattr(
        materials,
        "get_user_profile",
        lambda user_id: {
            "status": "not_found",
            "message": "User profile was not found.",
        },
    )

    result = materials.generate_materials_for_saved_records(
        user_id=999,
        application_id=1,
        save=False,
    )

    assert result["status"] == "not_found"


def test_generate_materials_for_saved_records_job_not_found(monkeypatch):
    monkeypatch.setattr(
        materials,
        "get_user_profile",
        lambda user_id: {
            "status": "success",
            "data": sample_user_profile(),
        },
    )
    monkeypatch.setattr(
        materials,
        "get_job_analysis",
        lambda application_id: {
            "status": "not_found",
            "message": "Job analysis record was not found.",
        },
    )

    result = materials.generate_materials_for_saved_records(
        user_id=1,
        application_id=999,
        save=False,
    )

    assert result["status"] == "not_found"