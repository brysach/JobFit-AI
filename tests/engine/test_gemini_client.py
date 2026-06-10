# tests/engine/test_gemini_client.py

from __future__ import annotations

import pytest

import src.engine.gemini_client as gemini_client


class FakeResponse:
    def __init__(self, text: str | None):
        self.text = text


class FakeModels:
    def __init__(self, response_text: str | None):
        self.response_text = response_text
        self.received_model = None
        self.received_contents = None

    def generate_content(self, model: str, contents: str):
        self.received_model = model
        self.received_contents = contents
        return FakeResponse(self.response_text)


class FakeClient:
    def __init__(self, api_key: str, response_text: str | None = "Generated text"):
        self.api_key = api_key
        self.models = FakeModels(response_text)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_call_gemini_success(monkeypatch):
    fake_client_holder = {}

    def fake_client_constructor(api_key: str):
        fake_client = FakeClient(api_key=api_key, response_text="Generated response")
        fake_client_holder["client"] = fake_client
        return fake_client

    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    monkeypatch.setenv("GEMINI_MODEL", "fake-model")
    monkeypatch.setattr(gemini_client.genai, "Client", fake_client_constructor)

    result = gemini_client.call_gemini("Analyze this job description.")

    assert result == "Generated response"
    assert fake_client_holder["client"].api_key == "fake-api-key"
    assert fake_client_holder["client"].models.received_model == "fake-model"
    assert (
        fake_client_holder["client"].models.received_contents
        == "Analyze this job description."
    )
    assert fake_client_holder["client"].closed is True


def test_call_gemini_uses_default_model(monkeypatch):
    fake_client_holder = {}

    def fake_client_constructor(api_key: str):
        fake_client = FakeClient(api_key=api_key, response_text="Generated response")
        fake_client_holder["client"] = fake_client
        return fake_client

    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setattr(gemini_client.genai, "Client", fake_client_constructor)

    result = gemini_client.call_gemini("Prompt text")

    assert result == "Generated response"
    assert fake_client_holder["client"].models.received_model == "gemini-2.5-flash"
    assert fake_client_holder["client"].closed is True


def test_call_gemini_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        gemini_client.call_gemini("Prompt text")


def test_call_gemini_empty_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "   ")

    with pytest.raises(RuntimeError):
        gemini_client.call_gemini("Prompt text")


def test_call_gemini_strips_api_key(monkeypatch):
    fake_client_holder = {}

    def fake_client_constructor(api_key: str):
        fake_client = FakeClient(api_key=api_key, response_text="Generated response")
        fake_client_holder["client"] = fake_client
        return fake_client

    monkeypatch.setenv("GEMINI_API_KEY", "  fake-api-key  ")
    monkeypatch.setattr(gemini_client.genai, "Client", fake_client_constructor)

    result = gemini_client.call_gemini("Prompt text")

    assert result == "Generated response"
    assert fake_client_holder["client"].api_key == "fake-api-key"
    assert fake_client_holder["client"].closed is True


def test_call_gemini_empty_response(monkeypatch):
    fake_client_holder = {}

    def fake_client_constructor(api_key: str):
        fake_client = FakeClient(api_key=api_key, response_text="")
        fake_client_holder["client"] = fake_client
        return fake_client

    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    monkeypatch.setattr(gemini_client.genai, "Client", fake_client_constructor)

    with pytest.raises(RuntimeError):
        gemini_client.call_gemini("Prompt text")

    assert fake_client_holder["client"].closed is True


def test_call_gemini_none_response_text(monkeypatch):
    fake_client_holder = {}

    def fake_client_constructor(api_key: str):
        fake_client = FakeClient(api_key=api_key, response_text=None)
        fake_client_holder["client"] = fake_client
        return fake_client

    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    monkeypatch.setattr(gemini_client.genai, "Client", fake_client_constructor)

    with pytest.raises(RuntimeError):
        gemini_client.call_gemini("Prompt text")

    assert fake_client_holder["client"].closed is True