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