# src/storage/google_sheets.py

from __future__ import annotations

import os

import gspread


def get_worksheet(worksheet_name: str | None = None):
    """Return a Google Sheets worksheet.

    If worksheet_name is None, return the first worksheet.
    Otherwise, return the worksheet with the given tab name.
    """

    gc = gspread.service_account(filename="service_account.json")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME", "JobFit-AI")
    sh = gc.open(sheet_name)

    if worksheet_name is None:
        return sh.get_worksheet(0)

    return sh.worksheet(worksheet_name)