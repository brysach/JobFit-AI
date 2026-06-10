# tests/storage/test_google_sheets.py

from __future__ import annotations

import src.storage.google_sheets as google_sheets


class FakeSpreadsheet:
    def __init__(self):
        self.requested_index = None
        self.requested_worksheet_name = None

    def get_worksheet(self, index: int):
        self.requested_index = index
        return f"worksheet-index-{index}"

    def worksheet(self, worksheet_name: str):
        self.requested_worksheet_name = worksheet_name
        return f"worksheet-{worksheet_name}"


class FakeGspreadClient:
    def __init__(self):
        self.opened_sheet_name = None
        self.spreadsheet = FakeSpreadsheet()

    def open(self, sheet_name: str):
        self.opened_sheet_name = sheet_name
        return self.spreadsheet


def test_get_worksheet_returns_first_worksheet_by_default(monkeypatch):
    fake_client = FakeGspreadClient()

    def fake_service_account(filename: str):
        assert filename == "service_account.json"
        return fake_client

    monkeypatch.setenv("GOOGLE_SHEET_NAME", "Test Sheet")
    monkeypatch.setattr(
        google_sheets.gspread,
        "service_account",
        fake_service_account,
    )

    result = google_sheets.get_worksheet()

    assert result == "worksheet-index-0"
    assert fake_client.opened_sheet_name == "Test Sheet"
    assert fake_client.spreadsheet.requested_index == 0


def test_get_worksheet_returns_named_worksheet(monkeypatch):
    fake_client = FakeGspreadClient()

    def fake_service_account(filename: str):
        assert filename == "service_account.json"
        return fake_client

    monkeypatch.setenv("GOOGLE_SHEET_NAME", "Test Sheet")
    monkeypatch.setattr(
        google_sheets.gspread,
        "service_account",
        fake_service_account,
    )

    result = google_sheets.get_worksheet("usersProfile")

    assert result == "worksheet-usersProfile"
    assert fake_client.opened_sheet_name == "Test Sheet"
    assert fake_client.spreadsheet.requested_worksheet_name == "usersProfile"


def test_get_worksheet_uses_default_sheet_name(monkeypatch):
    fake_client = FakeGspreadClient()

    def fake_service_account(filename: str):
        assert filename == "service_account.json"
        return fake_client

    monkeypatch.delenv("GOOGLE_SHEET_NAME", raising=False)
    monkeypatch.setattr(
        google_sheets.gspread,
        "service_account",
        fake_service_account,
    )

    result = google_sheets.get_worksheet("jobsAnalysis")

    assert result == "worksheet-jobsAnalysis"
    assert fake_client.opened_sheet_name == "JobFit-AI"