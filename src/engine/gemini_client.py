# src/engine/gemini_client.py

"""Gemini API wrapper for JobFit-AI.

Architecture position:
    engine -> Gemini API

This module provides one small wrapper around the Gemini client. It reads
the Gemini API key and model name from environment variables, sends a
prompt to Gemini, validates that a non-empty response was returned, and
closes the Gemini client after the request.

This module should not parse application-specific JSON. Other engine
modules are responsible for interpreting Gemini's text response.

Environment variables:
    GEMINI_API_KEY:
        Required. API key used to authenticate with Gemini.

    GEMINI_MODEL:
        Optional. Gemini model name. If this variable is not set, the
        module uses "gemini-2.5-flash".

Error contract:
    This module raises RuntimeError instead of returning response
    dictionaries because it is a low-level API wrapper. Engine modules
    catch these errors and convert them into user-facing status payloads
    such as "ai_error".
"""

from __future__ import annotations

import os

from google import genai


def call_gemini(prompt: str) -> str:
    """Call Gemini API and return the raw response text.

    Parameters:
        prompt (str): Prompt text sent to Gemini.

    Returns:
        str: Non-empty raw response text returned by Gemini.

    Raises:
        RuntimeError: If GEMINI_API_KEY is missing or blank.
        RuntimeError: If Gemini returns an empty response.

    Notes:
        This function does not clean Markdown code fences, parse JSON, or
        validate application-specific fields. The caller is responsible for
        interpreting the returned text.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key is None or api_key.strip() == "":
        raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

    api_key = api_key.strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text
    finally:
        client.close()