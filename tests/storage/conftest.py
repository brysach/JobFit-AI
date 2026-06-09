# tests/storage/conftest.py

from __future__ import annotations

import pytest

import src.storage.job_analysis_storage as job_analysis_storage
import src.storage.materials_storage as materials_storage
import src.storage.user_profile_storage as user_profile_storage


class _InMemoryWorksheet:
    def __init__(self, headers: list[str]):
        self._rows = [headers]

    def col_values(self, col: int) -> list[str]:
        values = []

        for row in self._rows:
            if len(row) >= col:
                values.append(str(row[col - 1]))

        return values

    def append_row(self, row: list) -> None:
        self._rows.append(row)

    def get_all_records(self) -> list[dict]:
        headers = self._rows[0]
        records = []

        for row in self._rows[1:]:
            record = {}

            for index, header in enumerate(headers):
                if index < len(row):
                    record[header] = row[index]
                else:
                    record[header] = ""

            records.append(record)

        return records

    def delete_rows(self, row_number: int) -> None:
        row_index = row_number - 1

        if row_index <= 0 or row_index >= len(self._rows):
            raise IndexError("Invalid row number.")

        del self._rows[row_index]


@pytest.fixture(autouse=True)
def in_memory_worksheets(monkeypatch):
    worksheets = {
        "jobsAnalysis": _InMemoryWorksheet(
            [
                "application_id",
                "company_name",
                "job_title",
                "required_skills",
                "keywords",
            ]
        ),
        "usersProfile": _InMemoryWorksheet(
            [
                "user_id",
                "name",
                "email",
                "phone_number",
                "university",
                "degree",
                "skills",
                "projects",
                "experience",
            ]
        ),
        "generatedMaterials": _InMemoryWorksheet(
            [
                "application_id",
                "user_id",
                "resume_skills",
                "resume_projects",
                "resume_experience",
                "cover_letter",
                "strengths",
                "weaknesses",
            ]
        ),
    }

    def fake_get_worksheet(worksheet_name: str | None = None):
        if worksheet_name is None:
            return worksheets["jobsAnalysis"]

        return worksheets[worksheet_name]

    monkeypatch.setattr(
        job_analysis_storage,
        "get_worksheet",
        fake_get_worksheet,
        raising=False,
    )

    monkeypatch.setattr(
        user_profile_storage,
        "get_worksheet",
        fake_get_worksheet,
        raising=False,
    )

    monkeypatch.setattr(
        materials_storage,
        "get_worksheet",
        fake_get_worksheet,
        raising=False,
    )

    monkeypatch.setattr(
        job_analysis_storage,
        "_get_job_analysis_worksheet",
        lambda: worksheets["jobsAnalysis"],
        raising=False,
    )

    monkeypatch.setattr(
        user_profile_storage,
        "_get_user_profile_worksheet",
        lambda: worksheets["usersProfile"],
        raising=False,
    )

    monkeypatch.setattr(
        materials_storage,
        "_get_generated_materials_worksheet",
        lambda: worksheets["generatedMaterials"],
        raising=False,
    )

    return worksheets