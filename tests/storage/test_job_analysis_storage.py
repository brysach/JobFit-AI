# tests/storage/test_job_analysis_storage.py

from __future__ import annotations

from src.storage.job_analysis_storage import get_job_analysis
from src.storage.job_analysis_storage import save_job_analysis


def valid_job_analysis() -> dict:
    return {
        "job_title": "Software Engineering Intern",
        "required_skills": ["Python", "Git"],
        "keywords": ["Python", "Git", "teamwork"],
    }


def test_save_job_analysis_success():
    result = save_job_analysis(valid_job_analysis())

    assert result["status"] == "success"
    assert result["application_id"] == 1


def test_save_job_analysis_generates_incrementing_ids():
    first_result = save_job_analysis(valid_job_analysis())
    second_result = save_job_analysis(valid_job_analysis())

    assert first_result["status"] == "success"
    assert second_result["status"] == "success"
    assert first_result["application_id"] == 1
    assert second_result["application_id"] == 2


def test_missing_required_fields_error():
    job_analysis = valid_job_analysis()
    del job_analysis["job_title"]

    result = save_job_analysis(job_analysis)

    assert result["status"] == "error"


def test_get_job_analysis_success():
    save_result = save_job_analysis(valid_job_analysis())
    application_id = save_result["application_id"]

    get_result = get_job_analysis(application_id)

    assert get_result["status"] == "success"
    assert get_result["data"]["application_id"] == application_id
    assert get_result["data"]["job_title"] == "Software Engineering Intern"
    assert get_result["data"]["required_skills"] == ["Python", "Git"]
    assert get_result["data"]["keywords"] == ["Python", "Git", "teamwork"]


def test_get_job_analysis_not_found():
    result = get_job_analysis(999)

    assert result["status"] == "not_found"
    assert result["message"] == "Job analysis record was not found."