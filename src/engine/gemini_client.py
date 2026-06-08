# src/engine/gemini_client.py

from __future__ import annotations

import os

from google import genai


def call_gemini(prompt: str) -> str:
    """Call Gemini API and return the raw response text."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

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