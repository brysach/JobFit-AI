# tests/interface/test_cli.py

from __future__ import annotations

import src.interface.cli as cli


def sample_success_response() -> dict:
    return {
        "status": "success",
        "data": {
            "job_title": "Software Engineering Intern",
            "required_skills": ["Python", "Git"],
            "preferred_skills": ["React"],
            "responsibilities": ["Build web applications", "Write tests"],
            "keywords": ["Python", "Git", "teamwork"],
        },
    }


def test_format_analysis_response_success():
    output = cli.format_analysis_response(sample_success_response())

    assert "Job Analysis" in output
    assert "Job Title: Software Engineering Intern" in output
    assert "- Python" in output
    assert "- Git" in output
    assert "- teamwork" in output


def test_format_analysis_response_error():
    response = {
        "status": "incomplete",
        "message": "Job description is required.",
    }

    output = cli.format_analysis_response(response)

    assert output == "Job description is required."


def test_analyze_without_saving(monkeypatch):
    monkeypatch.setattr(
        cli,
        "analyze_job_description",
        lambda job_description: sample_success_response(),
    )

    result = cli.analyze_and_optionally_save(
        "Software Engineering Intern job description",
        save=False,
    )

    assert result["status"] == "success"
    assert "save_status" not in result


def test_analyze_and_save_success(monkeypatch):
    saved_record = {}

    def fake_save_job_analysis(job_analysis: dict) -> str:
        saved_record.update(job_analysis)
        return "success"

    monkeypatch.setattr(
        cli,
        "analyze_job_description",
        lambda job_description: sample_success_response(),
    )

    monkeypatch.setattr(
        cli,
        "save_job_analysis",
        fake_save_job_analysis,
    )

    result = cli.analyze_and_optionally_save(
        "Software Engineering Intern job description",
        application_id=1,
        save=True,
    )

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert saved_record["application_id"] == 1
    assert saved_record["job_title"] == "Software Engineering Intern"
    assert saved_record["required_skills"] == ["Python", "Git"]
    assert saved_record["keywords"] == ["Python", "Git", "teamwork"]


def test_save_without_application_id_returns_error(monkeypatch):
    monkeypatch.setattr(
        cli,
        "analyze_job_description",
        lambda job_description: sample_success_response(),
    )

    result = cli.analyze_and_optionally_save(
        "Software Engineering Intern job description",
        save=True,
    )

    assert result["status"] == "missing_application_id"
    assert result["message"] == "Application ID is required to save the job analysis."