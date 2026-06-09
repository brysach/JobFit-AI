# tests/interface/test_job_analysis_cli.py

from __future__ import annotations

import builtins
import src.interface.job_analysis_cli as job_analysis_cli

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
    output = job_analysis_cli.format_analysis_response(sample_success_response())

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

    output = job_analysis_cli.format_analysis_response(response)

    assert output == "Job description is required."

def test_run_job_analysis_flow_generate_and_save(monkeypatch):
    inputs = iter(
        [
            "Software Engineering Intern",
            "",
            "Responsibilities:",
            "Build Python applications.",
            "END",
            "y",
            "y",
        ]
    )

    captured_saved_data = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_analyze_job_description(job_description: str) -> dict:
        return {
            "status": "success",
            "data": {
                "job_title": "Software Engineering Intern",
                "required_skills": ["Python"],
                "preferred_skills": [],
                "responsibilities": ["Build Python applications"],
                "keywords": ["Python", "internship"],
            },
        }

    def fake_save_existing_job_analysis(analysis_data: dict) -> dict:
        captured_saved_data.update(analysis_data)
        return {
            "status": "success",
            "save_status": "success",
            "application_id": 1,
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        job_analysis_cli,
        "analyze_job_description",
        fake_analyze_job_description,
    )
    monkeypatch.setattr(
        job_analysis_cli,
        "save_existing_job_analysis",
        fake_save_existing_job_analysis,
    )

    result = job_analysis_cli.run_job_analysis_flow()

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert captured_saved_data["job_title"] == "Software Engineering Intern"
    assert captured_saved_data["required_skills"] == ["Python"]

def test_run_job_analysis_flow_regenerates_input_when_user_says_no(monkeypatch):
    inputs = iter(
        [
            "First job description",
            "END",
            "n",
            "Second job description",
            "END",
            "y",
            "n",
        ]
    )

    analyzed_descriptions = []

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_analyze_job_description(job_description: str) -> dict:
        analyzed_descriptions.append(job_description)
        return {
            "status": "success",
            "data": {
                "job_title": "Second Job",
                "required_skills": ["Python"],
                "preferred_skills": [],
                "responsibilities": ["Build software"],
                "keywords": ["Python"],
            },
        }

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        job_analysis_cli,
        "analyze_job_description",
        fake_analyze_job_description,
    )

    result = job_analysis_cli.run_job_analysis_flow()

    assert result["status"] == "success"
    assert analyzed_descriptions == ["Second job description"]