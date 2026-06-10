# src/interface/input_utils.py

"""Shared input helpers for command-line interface flows.

Architecture position:
    interface helper

This module contains small reusable helpers for command-line input.
It supports the shared BACK behavior used across the interface layer,
so feature flows can return to the main menu without duplicating the
same cancellation logic.

This module does not call the engine, storage, Gemini, or export layers.
"""

from __future__ import annotations


BACK_COMMANDS = {
    "back",
    "b",
    "menu",
}


def is_back_command(text: str) -> bool:
    """Return True if the user wants to return to the main menu.

    Parameters:
        text (str): User-entered text from the terminal.

    Returns:
        bool: True if text matches one of the accepted back commands;
        otherwise, False.

        Accepted back commands:
            - "back"
            - "b"
            - "menu"

        The comparison is case-insensitive and ignores surrounding
        whitespace.
    """

    return text.strip().lower() in BACK_COMMANDS


def cancelled_response() -> dict:
    """Return a standard cancelled response payload.

    Parameters:
        None.

    Returns:
        dict: Standard cancellation response.

        Return value:
            {
                "status": "cancelled",
                "message": "Returned to main menu.",
            }
    """

    return {
        "status": "cancelled",
        "message": "Returned to main menu.",
    }


def input_or_back(prompt: str) -> str | None:
    """Read one input value or detect a back command.

    Parameters:
        prompt (str): Prompt text displayed to the user.

    Returns:
        str | None: User-entered text if the user does not enter a back
        command; otherwise, None.

        Possible return values:
            str:
                The original input value entered by the user.

            None:
                The user entered one of the accepted back commands.
    """

    value = input(prompt)

    if is_back_command(value):
        return None

    return value


def print_back_instruction() -> None:
    """Print the shared back instruction.

    Parameters:
        None.

    Returns:
        None: This function only prints a message to the terminal.
    """

    print("Type BACK at any prompt to return to the main menu.")