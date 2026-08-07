# _client.py
# Lecture 2 — shared helper: one place to build an authenticated Groq client.
#
# DevOps analogy: this is the same pattern as a shared "auth client" module
# you'd write once in a microservices codebase -- one function that reads a
# credential from the environment and hands back an authenticated client, so
# no service repeats that boilerplate. Reused unchanged from Lecture 1 --
# this lecture only needs Groq for the small RAG-preview bonus at the end
# of demo 3; everything else is local embeddings + Chroma, no LLM call.

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# A small, fast, cheap model -- good fit for a lecture that fires off many
# rapid raw API calls back-to-back. Swap this one line to change the model
# for every demo in this lecture.
DEFAULT_MODEL = "llama-3.1-8b-instant"


def get_client() -> Groq:
    """
    Return an authenticated Groq client, or fail loudly with a clear
    instruction if no API key is configured.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )
    return Groq(api_key=GROQ_API_KEY)
