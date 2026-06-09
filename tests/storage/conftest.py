# tests/storage/conftest.py

from __future__ import annotations

import pytest

import src.storage.job_analysis_storage as job_analysis_storage
import src.storage.user_profile_storage as user_profile_storage
import src.storage.materials_storage as materials_storage


class _InMemoryWorksheet:
    def __init__(self, headers: list[str]):
        self._rows = [headers]

    def col_values(self, col: int) -> list[str]:
        return [str(row[col - 1]) for row in self._rows if len(row) >= col]

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
            ["application_id", "job_title", "required_skills", "keywords"]
        ),
        "usersProfile": _InMemoryWorksheet(
            ["user_id", "name", "education", "skills", "projects", "experience"]
        ),
        "generatedMaterials": _InMemoryWorksheet(
            ["application_id", "user_id", "resume_bullets", "cover_letter"]
        ),
    }

    def fake_get_worksheet(worksheet_name: str):
        return worksheets[worksheet_name]

    monkeypatch.setattr(
        job_analysis_storage,
        "get_worksheet",
        fake_get_worksheet,
    )

    monkeypatch.setattr(
        user_profile_storage,
        "get_worksheet",
        fake_get_worksheet,
    )

    monkeypatch.setattr(
        materials_storage,
        "get_worksheet",
        fake_get_worksheet,
    )