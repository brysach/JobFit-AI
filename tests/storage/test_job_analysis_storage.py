# tests/storage/test_storage.py

from __future__ import annotations

from src.storage.job_analysis_storage import save_job_analysis


def valid_job_analysis() -> dict:
    return {
        "application_id": 1,
        "job_title": "Software Engineering Intern",
        "required_skills": ["Python", "Git"],
        "keywords": ["Python", "Git", "teamwork"],
    }


def test_save_job_analysis_success():
    result = save_job_analysis(valid_job_analysis())

    assert result == "success"


def test_save_duplicate_job_analysis_exists():
    job_analysis = valid_job_analysis()

    first_result = save_job_analysis(job_analysis)
    second_result = save_job_analysis(job_analysis)

    assert first_result == "success"
    assert second_result == "exists"


def test_missing_required_fields_error():
    job_analysis = valid_job_analysis()
    del job_analysis["application_id"]

    result = save_job_analysis(job_analysis)

    assert result == "error"