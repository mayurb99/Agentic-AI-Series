# _client.py
# Lecture 4 — shared helper: one place to build the LangChain chat model.
#
# THIS FILE IS THE WHOLE LECTURE, IN MINIATURE.
# ------------------------------------------------
# Lectures 1-3 built `get_client()` around the raw `groq` SDK -- you called
# `client.chat.completions.create(...)` yourself, every time, and handled
# the response shape yourself. From this lecture on, `get_llm()` returns a
# LangChain `ChatGroq` object instead -- a `Runnable`, the same interface
# every other LangChain component implements. That one change is what
# unlocks the pipe operator (`|`), `.batch()`, and `.stream()` that
# demo_1 and demo_2 build on -- none of that exists on the raw SDK client.
#
# DevOps analogy: this is the same shared "auth client" pattern as every
# previous lecture's `_client.py` -- one function, one place credentials are
# read from the environment. What changed is what that function hands back:
# a raw SDK client before, a framework-native Runnable now.

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Same small, fast, cheap model used since Lecture 1 -- swap this one line
# to change the model for every demo in this lecture.
DEFAULT_MODEL = "llama-3.1-8b-instant"


def get_llm(temperature: float = 0, **kwargs) -> ChatGroq:
    """
    Return a LangChain ChatGroq chat model, or fail loudly with a clear
    instruction if no API key is configured.

    Unlike Lecture 3's get_client(), which returned a raw SDK object you
    called .chat.completions.create() on, this returns a Runnable -- it
    supports .invoke(), .batch(), .stream(), AND the `|` pipe operator,
    all of which demo_1 and demo_2 use directly.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )
    return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=temperature, **kwargs)
