import os
from groq import Groq

def _client() -> Groq:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing. Put it in backend/.env or env vars.")
    return Groq(api_key=key)

def generate_text(system: str, user: str) -> str:
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    resp = _client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()
