import json
import os

from prompt_templates import RESPONSE_SCHEMA, SYSTEM_PROMPT, build_user_prompt

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")


class GeminiUnavailableError(RuntimeError):
    pass


def call_gemini(fused_dataset: dict, detector_signals: list[dict]) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiUnavailableError("GEMINI_API_KEY not set")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    user_prompt = build_user_prompt(fused_dataset, detector_signals)

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0.2,
        ),
    )

    return json.loads(response.text)