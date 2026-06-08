# tests/storage/conftest.py

from __future__ import annotations

import pytest

import src.storage.job_analysis_storage as job_analysis_storage


class _InMemoryWorksheet:
    def __init__(self):
        self._rows = [
            ["application_id", "job_title", "required_skills", "keywords"]
        ]

    def col_values(self, col: int) -> list[str]:
        return [str(row[col - 1]) for row in self._rows if len(row) >= col]

    def append_row(self, row: list) -> None:
        self._rows.append(row)


@pytest.fixture(autouse=True)
def in_memory_worksheet(monkeypatch):
    worksheet = _InMemoryWorksheet()
    monkeypatch.setattr(
        job_analysis_storage,
        "get_worksheet",
        lambda worksheet_name=None: worksheet,
    )