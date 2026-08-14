# demo_4_rag_langchain_e2e.py
# Lecture 4 -- Demo 4: End-to-end RAG with LangChain (every step)
#
# THE BIG IDEA
# -------------
# Lecture 3 built RAG in pure Python (pypdf, hand chunking, raw Chroma, raw Groq).
# This demo does the SAME loop with LangChain pieces for every step:
#
#   1. Load     -> PyPDFLoader
#   2. Split    -> RecursiveCharacterTextSplitter
#   3. Embed+Store -> HuggingFaceEmbeddings + Chroma
#   4. Retrieve -> vectorstore.as_retriever(k=3)
#   5. Prompt+LLM -> ChatPromptTemplate + ChatGroq + StrOutputParser
#   6. Chain    -> LCEL | wire-up, then .invoke() on a few questions
#
# DEVOPS FLAVOR (light)
# ---------------------
# Same runbook Q&A idea as Lecture 3 -- OOMKilled, postmortem, canary.

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*langchain-community.*")

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEMOS_DIR = Path(__file__).resolve().parent
LECTURE4 = DEMOS_DIR.parent
PDF_CANDIDATES = [
    LECTURE4.parent / "lecture3" / "devops_runbook.pdf",
    LECTURE4 / "devops_runbook.pdf",
]
PERSIST_DIR = str(LECTURE4 / "chroma_store_l4_e2e")
COLLECTION_NAME = "runbook_rag_l4_langchain"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def show_l3_vs_l4() -> None:
    print_header("L3 (hand-built)  vs  L4 (LangChain) -- same RAG loop")
    print(
        """
  Lecture 3 (by hand)                 Lecture 4 (LangChain)
  ------------------------------      ------------------------------------
  PdfReader + extract_text()          PyPDFLoader.load()
  sentence_aware_chunks(...)          RecursiveCharacterTextSplitter
  chromadb + SentenceTransformer      Chroma + HuggingFaceEmbeddings
  collection.query(...)               retriever = vs.as_retriever(k=3)
  f-string + groq SDK unpack          prompt | llm | StrOutputParser
  hand-written ask() helper           one LCEL chain.invoke(question)

  Same idea: load -> split -> embed/store -> retrieve -> prompt -> answer.
  Today every step uses a LangChain component.
"""
    )


def format_docs(docs) -> str:
    """Turn retrieved Documents into numbered context for the prompt."""
    parts = []
    for i, doc in enumerate(docs, 1):
        parts.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(parts)


def main() -> None:
    print()
    print("LECTURE 4 -- DEMO 4")
    print("End-to-end RAG with LangChain")
    print("=" * 70)

    try:
        llm = get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    show_l3_vs_l4()

    # ------------------------------------------------------------------
    # STEP 1: Load documents
    # ------------------------------------------------------------------
    print_header("STEP 1: Load documents (PyPDFLoader)")
    pdf_path = next((p for p in PDF_CANDIDATES if p.exists()), None)
    if pdf_path is None:
        print("ERROR: devops_runbook.pdf not found under lecture3/ (or lecture4/).")
        sys.exit(1)

    docs = PyPDFLoader(str(pdf_path)).load()
    print(f"Loaded {len(docs)} page Document(s) from '{pdf_path.name}'.")
    print(f"Example metadata: {docs[0].metadata}")

    # ------------------------------------------------------------------
    # STEP 2: Split
    # ------------------------------------------------------------------
    print_header("STEP 2: Split (RecursiveCharacterTextSplitter)")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks (size=500, overlap=50).")
    print(f"Chunk[0] preview: {chunks[0].page_content[:100]!r}...")

    # ------------------------------------------------------------------
    # STEP 3: Embed + store
    # ------------------------------------------------------------------
    print_header("STEP 3: Embed + store (HuggingFaceEmbeddings + Chroma)")
    print(f"Embedding model: {EMBED_MODEL}")
    print("(First run may download ~80 MB, then it is cached locally.)")

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
    )
    print(f"Stored chunks in Chroma at '{PERSIST_DIR}'.")

    # ------------------------------------------------------------------
    # STEP 4: Retriever
    # ------------------------------------------------------------------
    print_header("STEP 4: Retriever (.as_retriever(k=3))")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print("retriever = vectorstore.as_retriever(search_kwargs={'k': 3})")
    print("On each question it returns the top 3 Documents by meaning.")

    # ------------------------------------------------------------------
    # STEP 5: Prompt + LLM + parser
    # ------------------------------------------------------------------
    print_header("STEP 5: Prompt + LLM (ChatGroq) + StrOutputParser")
    prompt = ChatPromptTemplate.from_template(
        "Answer using ONLY the numbered context. Cite [n] after every claim.\n"
        "If the context does not contain the answer, say so.\n\n"
        "Context:\n{context}\n\nQuestion: {question}"
    )
    parser = StrOutputParser()
    print("prompt = ChatPromptTemplate.from_template(...)")
    print("llm    = ChatGroq (from get_llm())")
    print("parser = StrOutputParser()")

    # ------------------------------------------------------------------
    # STEP 6: LCEL chain wire-up
    # ------------------------------------------------------------------
    print_header("STEP 6: LCEL chain wire-up")
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
    print(
        "\n  rag_chain = (\n"
        "      {\"context\": retriever | format_docs,\n"
        "       \"question\": RunnablePassthrough()}\n"
        "      | prompt | llm | StrOutputParser()\n"
        "  )\n"
    )
    print("One .invoke(question) runs retrieve -> prompt -> LLM -> string.")

    # ------------------------------------------------------------------
    # STEP 7: Ask a few DevOps questions (+ simple citations in the prompt)
    # ------------------------------------------------------------------
    print_header("STEP 7: Ask 3 simple runbook questions")
    questions = [
        "What should I do if a pod shows OOMKilled?",
        "How long do I have to write a postmortem after a severity-1 incident?",
        "Our canary deployment's error rate spiked right after release, what now?",
    ]
    for question in questions:
        print(f"\n  Q: {question}")
        # Optional peek at what was retrieved (keeps citations easy to check)
        retrieved = retriever.invoke(question)
        print("  Retrieved:")
        for i, doc in enumerate(retrieved, 1):
            preview = doc.page_content.replace("\n", " ").strip()[:90]
            print(f"    [{i}] {preview}...")
        answer = rag_chain.invoke(question)
        print(f"  A: {answer}")

    print_header("RECAP")
    print(
        "\n- Every RAG step used a LangChain component (loaders through chain).\n"
        "- RecursiveCharacterTextSplitter is the everyday default splitter.\n"
        "- Retriever + LCEL replaces the hand-written retrieve/prompt/SDK loop.\n"
        "- Later lectures assume you know this pipeline -- they will not re-teach it."
    )


if __name__ == "__main__":
    main()
