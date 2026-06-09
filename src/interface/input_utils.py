# src/interface/input_utils.py

from __future__ import annotations


BACK_COMMANDS = {
    "back",
    "b",
    "menu",
}


def is_back_command(text: str) -> bool:
    """Return True if the user wants to return to the main menu."""

    return text.strip().lower() in BACK_COMMANDS


def cancelled_response() -> dict:
    """Return a standard cancelled response."""

    return {
        "status": "cancelled",
        "message": "Returned to main menu.",
    }


def input_or_back(prompt: str) -> str | None:
    """Read one input value.

    Return None if the user chooses to go back.
    """

    value = input(prompt)

    if is_back_command(value):
        return None

    return value


def print_back_instruction() -> None:
    """Print the shared back instruction."""

    print("Type BACK at any prompt to return to the main menu.")