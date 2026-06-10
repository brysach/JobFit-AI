# src/storage/google_sheets.py

"""Shared Google Sheets connection helper.

Architecture position:
    storage -> Google Sheets

This module centralizes the Google Sheets connection logic used by the
storage layer. Other storage modules call get_worksheet() to access a
specific worksheet tab.

This module uses service_account.json for authentication and reads the
Google Sheet name from the GOOGLE_SHEET_NAME environment variable. If
GOOGLE_SHEET_NAME is not set, the default sheet name is "JobFit-AI".

This module should not validate application records, parse stored rows,
call Gemini, or format terminal output. Its only responsibility is to
return the requested Google Sheets worksheet object.
"""

from __future__ import annotations

import os

import gspread


def get_worksheet(worksheet_name: str | None = None):
    """Return a Google Sheets worksheet.

    Parameters:
        worksheet_name (str | None): Name of the worksheet tab to open.
        If None, the first worksheet in the Google Sheet is returned.

    Returns:
        gspread.worksheet.Worksheet: Google Sheets worksheet object.

        Possible return values:
            If worksheet_name is None:
                Returns the first worksheet in the spreadsheet.

            If worksheet_name is a string:
                Returns the worksheet tab with that exact name.

    Raises:
        FileNotFoundError: If service_account.json is missing.
        gspread.exceptions.SpreadsheetNotFound: If the configured Google
        Sheet cannot be found or the service account does not have access.
        gspread.exceptions.WorksheetNotFound: If worksheet_name is provided
        but no worksheet with that name exists.
        Exception: If Google Sheets authentication or API access fails for
        another reason.

    Environment variables:
        GOOGLE_SHEET_NAME:
            Optional. Name of the Google Sheet to open. If missing, the
            default value is "JobFit-AI".
    """

    gc = gspread.service_account(filename="service_account.json")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME", "JobFit-AI")
    sh = gc.open(sheet_name)

    if worksheet_name is None:
        return sh.get_worksheet(0)

    return sh.worksheet(worksheet_name)