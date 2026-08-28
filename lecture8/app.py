# app.py
# Lecture 8 — Streamlit UI for the on-call runbook helper
#
# From lecture8/:
#   1) python ingest.py
#   2) streamlit run app.py
#
# Needs: GROQ_API_KEY in lecture8/.env

from __future__ import annotations

import json
import uuid

import streamlit as st

from agent import ask_chat, ask_ticket, build_chat_agent

st.set_page_config(
    page_title="On-Call Runbook Helper | Lecture 8",
    layout="centered",
)

st.title("On-Call Runbook Helper")
st.caption("RAG tool searches data/ via Chroma. Tools + memory (thread_id). Groq + LangChain.")


def new_thread_id() -> str:
    return f"ui-{uuid.uuid4().hex[:8]}"


def current_messages() -> list:
    return st.session_state.chats[st.session_state.thread_id]


# Many chats keyed by thread_id (New chat does NOT wipe others)
if "chats" not in st.session_state:
    tid = new_thread_id()
    st.session_state.thread_id = tid
    st.session_state.chats = {tid: []}
elif "thread_id" not in st.session_state:
    st.session_state.thread_id = next(iter(st.session_state.chats))

with st.sidebar:
    st.subheader("Thread ID")
    st.code(st.session_state.thread_id)
    st.caption("New chat keeps your old chats — click one below to reopen.")

    if st.button("New chat"):
        tid = new_thread_id()
        st.session_state.chats[tid] = []
        st.session_state.thread_id = tid
        st.rerun()

    st.markdown("**Your chats**")
    for tid in reversed(list(st.session_state.chats.keys())):
        label = f"→ {tid}" if tid == st.session_state.thread_id else tid
        if st.button(label, key=f"open_{tid}"):
            st.session_state.thread_id = tid
            st.rerun()

    if st.button("Delete this chat"):
        tid = st.session_state.thread_id
        del st.session_state.chats[tid]
        if not st.session_state.chats:
            tid = new_thread_id()
            st.session_state.chats[tid] = []
            st.session_state.thread_id = tid
        else:
            st.session_state.thread_id = list(st.session_state.chats.keys())[-1]
        st.rerun()

    ticket_mode = st.checkbox("Ticket mode", value=False)

    with st.expander("Custom thread id"):
        custom = st.text_input("Override id", key="thread_id_edit", label_visibility="collapsed")
        if st.button("Use this id") and custom.strip():
            tid = custom.strip()
            if tid not in st.session_state.chats:
                st.session_state.chats[tid] = []
            st.session_state.thread_id = tid
            st.rerun()

if "chat_agent" not in st.session_state:
    try:
        st.session_state.chat_agent = build_chat_agent()
        st.session_state.agent_error = None
    except RuntimeError as exc:
        st.session_state.agent_error = str(exc)

if st.session_state.get("agent_error"):
    st.error(st.session_state.agent_error)
    st.stop()

messages = current_messages()

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("ticket_json"):
            st.code(msg["ticket_json"], language="json")

prompt = st.chat_input("Ask the on-call helper…")
if prompt:
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                if ticket_mode:
                    ticket = ask_ticket(
                        st.session_state.chat_agent,
                        st.session_state.thread_id,
                        prompt,
                    )
                    if ticket is None:
                        text = "Could not build a structured ticket."
                        ticket_json = None
                        st.markdown(text)
                    else:
                        text = (
                            f"**Ticket filed:** {ticket.title}\n\n"
                            f"- Service: `{ticket.service_name}`\n"
                            f"- Severity: `{ticket.severity}`\n"
                            f"- Needs approval: `{ticket.needs_human_approval}`\n\n"
                            f"{ticket.status_summary}\n\n"
                            f"**Action:** {ticket.recommended_action}"
                        )
                        ticket_json = json.dumps(ticket.model_dump(), indent=2)
                        st.markdown(text)
                        st.code(ticket_json, language="json")
                else:
                    text = ask_chat(
                        st.session_state.chat_agent,
                        st.session_state.thread_id,
                        prompt,
                    )
                    ticket_json = None
                    st.markdown(text)
            except Exception as exc:
                text = f"Error calling agent: {exc}"
                ticket_json = None
                st.error(text)

    messages.append(
        {"role": "assistant", "content": text, "ticket_json": ticket_json}
    )
