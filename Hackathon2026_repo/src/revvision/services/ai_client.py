from __future__ import annotations

import os


def _client():
    try:
        from openai import OpenAI
    except ModuleNotFoundError as ex:
        raise RuntimeError(
            "OpenAI SDK is not installed. Run `pip install -r requirements.txt`."
        ) from ex

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add your OpenAI API key as an environment variable."
        )

    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def run_chat(model: str, system_prompt: str, user_prompt: str) -> str:
    client = _client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""
