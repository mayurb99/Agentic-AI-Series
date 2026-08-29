# _client.py
# Tiny helper: load GROQ_API_KEY and build ChatGroq for Demo 3.
# Demos 1–2 do not use this file (they are offline).

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load demos/.env first, then a parent .env if present
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "openai/gpt-oss-120b"


def get_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq model. Raises a clear error if the key is missing."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )
    return ChatGroq(
        model=MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=256,
    )
