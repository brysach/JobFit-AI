# tests/interface/test_input_utils.py

from __future__ import annotations

import builtins

import src.interface.input_utils as input_utils


def test_is_back_command_accepts_back_words():
    assert input_utils.is_back_command("BACK") is True
    assert input_utils.is_back_command("back") is True
    assert input_utils.is_back_command("b") is True
    assert input_utils.is_back_command("menu") is True


def test_is_back_command_rejects_normal_text():
    assert input_utils.is_back_command("Bryan") is False
    assert input_utils.is_back_command("Python") is False
    assert input_utils.is_back_command("yes") is False


def test_cancelled_response():
    response = input_utils.cancelled_response()

    assert response["status"] == "cancelled"
    assert response["message"] == "Returned to main menu."


def test_input_or_back_returns_none_for_back(monkeypatch):
    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt="": "BACK",
    )

    result = input_utils.input_or_back("Enter something: ")

    assert result is None


def test_input_or_back_returns_user_input(monkeypatch):
    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt="": "Bryan Estrada",
    )

    result = input_utils.input_or_back("Enter something: ")

    assert result == "Bryan Estrada"