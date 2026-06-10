# tests/storage/test_job_analysis_storage.py

from __future__ import annotations

import src.storage.job_analysis_storage as job_analysis_storage

from src.storage.job_analysis_storage import delete_job_analysis_by_row
from src.storage.job_analysis_storage import get_job_analysis
from src.storage.job_analysis_storage import list_job_analyses
from src.storage.job_analysis_storage import save_job_analysis


def valid_job_analysis() -> dict:
    return {
        "company_name": "TechStart",
        "job_title": "Software Engineering Intern",
        "required_skills": ["Python", "Git"],
        "keywords": ["Python", "Git", "teamwork"],
    }


def second_valid_job_analysis() -> dict:
    return {
        "company_name": "DataWorks",
        "job_title": "Data Analyst Intern",
        "required_skills": ["Python", "pandas", "SQL"],
        "keywords": ["data", "visualization", "machine learning"],
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


def test_save_job_analysis_rejects_non_dict_payload():
    result = save_job_analysis("not a dictionary")

    assert result["status"] == "error"


def test_missing_required_fields_error():
    job_analysis = valid_job_analysis()
    del job_analysis["company_name"]

    result = save_job_analysis(job_analysis)

    assert result["status"] == "error"


def test_save_job_analysis_storage_error(monkeypatch):
    def fake_get_worksheet(worksheet_name: str | None = None):
        raise RuntimeError("Google Sheets failed")

    def fake_get_job_analysis_worksheet():
        raise RuntimeError("Google Sheets failed")

    monkeypatch.setattr(
        job_analysis_storage,
        "get_worksheet",
        fake_get_worksheet,
        raising=False,
    )

    monkeypatch.setattr(
        job_analysis_storage,
        "_get_job_analysis_worksheet",
        fake_get_job_analysis_worksheet,
        raising=False,
    )

    result = save_job_analysis(valid_job_analysis())

    assert result["status"] == "error"


def test_get_job_analysis_success():
    save_result = save_job_analysis(valid_job_analysis())
    application_id = save_result["application_id"]

    get_result = get_job_analysis(application_id)

    assert get_result["status"] == "success"
    assert get_result["data"]["company_name"] == "TechStart"
    assert get_result["data"]["application_id"] == application_id
    assert get_result["data"]["job_title"] == "Software Engineering Intern"
    assert get_result["data"]["required_skills"] == ["Python", "Git"]
    assert get_result["data"]["keywords"] == ["Python", "Git", "teamwork"]


def test_get_job_analysis_not_found():
    result = get_job_analysis(999)

    assert result["status"] == "not_found"
    assert result["message"] == "Job analysis record was not found."


def test_list_job_analyses_success():
    save_job_analysis(valid_job_analysis())
    save_job_analysis(second_valid_job_analysis())

    result = list_job_analyses()

    assert result["status"] == "success"
    assert len(result["data"]) == 2

    assert result["data"][0]["row_number"] == 2
    assert result["data"][0]["application_id"] == 1
    assert result["data"][0]["company_name"] == "TechStart"
    assert result["data"][0]["job_title"] == "Software Engineering Intern"
    assert result["data"][0]["required_skills"] == ["Python", "Git"]
    assert result["data"][0]["keywords"] == ["Python", "Git", "teamwork"]

    assert result["data"][1]["row_number"] == 3
    assert result["data"][1]["application_id"] == 2
    assert result["data"][1]["company_name"] == "DataWorks"
    assert result["data"][1]["job_title"] == "Data Analyst Intern"
    assert result["data"][1]["required_skills"] == ["Python", "pandas", "SQL"]
    assert result["data"][1]["keywords"] == [
        "data",
        "visualization",
        "machine learning",
    ]


def test_list_job_analyses_empty_success():
    result = list_job_analyses()

    assert result["status"] == "success"
    assert result["data"] == []


def test_list_job_analyses_storage_error(monkeypatch):
    def fake_get_worksheet(worksheet_name: str | None = None):
        raise RuntimeError("Google Sheets failed")

    def fake_get_job_analysis_worksheet():
        raise RuntimeError("Google Sheets failed")

    monkeypatch.setattr(
        job_analysis_storage,
        "get_worksheet",
        fake_get_worksheet,
        raising=False,
    )

    monkeypatch.setattr(
        job_analysis_storage,
        "_get_job_analysis_worksheet",
        fake_get_job_analysis_worksheet,
        raising=False,
    )

    result = list_job_analyses()

    assert result["status"] == "error"
    assert result["message"] == "Could not retrieve job analyses."


def test_delete_job_analysis_by_row_success():
    save_job_analysis(valid_job_analysis())

    delete_result = delete_job_analysis_by_row(2)
    list_result = list_job_analyses()

    assert delete_result["status"] == "success"
    assert list_result["status"] == "success"
    assert list_result["data"] == []


def test_delete_job_analysis_by_row_invalid_row_error():
    result = delete_job_analysis_by_row(99)

    assert result["status"] == "error"


def test_delete_job_analysis_by_row_storage_error(monkeypatch):
    def fake_get_worksheet(worksheet_name: str | None = None):
        raise RuntimeError("Google Sheets failed")

    def fake_get_job_analysis_worksheet():
        raise RuntimeError("Google Sheets failed")

    monkeypatch.setattr(
        job_analysis_storage,
        "get_worksheet",
        fake_get_worksheet,
        raising=False,
    )

    monkeypatch.setattr(
        job_analysis_storage,
        "_get_job_analysis_worksheet",
        fake_get_job_analysis_worksheet,
        raising=False,
    )

    result = delete_job_analysis_by_row(2)

    assert result["status"] == "error"