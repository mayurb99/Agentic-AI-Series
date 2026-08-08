# demo_3_rag_pipeline_pdf.py
# Lecture 3 -- Demo 3: Full RAG loop on a PDF
#
# THE BIG IDEA
# -------------
# RAG = Retrieval-Augmented Generation. Plain English loop:
#   1. Load PDF
#   2. Chunk
#   3. Embed + store in Chroma
#   4. Retrieve top chunks
#   5. Build prompt with context
#   6. Call Groq
#   7. Print answer + citations
#
# This file does that end-to-end on a real PDF, in pure Python (no LangChain).
#
# SIMPLE ANALOGY
# --------------
# Citations -> "show your sources" / link a claim back to the chunk it came from

import sys

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

from _chunking import sentence_aware_chunks
from _client import DEFAULT_MODEL, get_client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PDF_PATH = "devops_runbook.pdf"
PERSIST_DIR = "./chroma_store_demo3"
COLLECTION_NAME = "runbook_rag"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    print()
    print("LECTURE 3 -- DEMO 3 (THE REQUIRED DEMO)")
    print("Full RAG on a PDF: chunk -> embed -> retrieve -> answer with sources")
    print("=" * 70)

    # Need Groq for the answer step.
    try:
        groq_client = get_client()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    # ==================================================================
    # STEP 1: Load the PDF
    # ==================================================================
    print_header("STEP 1: Load the PDF")

    reader = PdfReader(PDF_PATH)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text is None:
            page_text = ""
        pages.append(page_text)

    full_text = "\n".join(pages)
    print(f"Loaded '{PDF_PATH}': {len(reader.pages)} pages, {len(full_text):,} characters.")

    # ==================================================================
    # STEP 2: Chunk the text (sentence-aware, from Demo 1)
    # ==================================================================
    print_header("STEP 2: Chunk the text")

    chunk_texts = sentence_aware_chunks(full_text, target_size=350)
    chunk_ids = []
    for i in range(len(chunk_texts)):
        chunk_ids.append("chunk_" + str(i))

    print(f"Produced {len(chunk_texts)} sentence-aware chunks.")
    print(f"Example chunk [0]: \"{chunk_texts[0][:120]}...\"")

    # ==================================================================
    # STEP 3: Embed + store in Chroma (same idea as Lecture 2)
    # ==================================================================
    print_header("STEP 3: Embed + store in Chroma")

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    if collection.count() == 0:
        print(f"Embedding and storing {len(chunk_texts)} chunks (first run)...")
        collection.add(documents=chunk_texts, ids=chunk_ids)
    else:
        print(f"Loaded {collection.count()} chunks already stored in '{PERSIST_DIR}'.")

    # ==================================================================
    # STEPS 4-7: For each question -- retrieve, prompt, answer, cite
    # ==================================================================
    questions = [
        "What does OOMKilled mean, and what exit code does it show?",
        "How many business days after resolution for a written severity-1 postmortem?",
        "Our canary deployment's error rate spiked right after release, what now?",
    ]

    for question in questions:
        print_header("STEPS 4-7: Retrieve -> Prompt -> Answer -> Citations")
        print(f"\nQuestion: \"{question}\"")

        # STEP 4: Retrieve top chunks by meaning (Chroma, like Lecture 2)
        print("\n--- STEP 4: Retrieve top 3 chunks ---")
        results = collection.query(query_texts=[question], n_results=3)
        retrieved_texts = results["documents"][0]
        retrieved_ids = results["ids"][0]

        for i in range(len(retrieved_texts)):
            preview = retrieved_texts[i][:110]
            print(f"  [{i + 1}] ({retrieved_ids[i]}) \"{preview}...\"")

        # STEP 5: Build a prompt that includes the retrieved context
        print("\n--- STEP 5: Build the prompt with numbered context ---")
        context_parts = []
        for i in range(len(retrieved_texts)):
            context_parts.append("[" + str(i + 1) + "] " + retrieved_texts[i])
        numbered_context = "\n\n".join(context_parts)

        system_msg = (
            "Answer using ONLY the numbered context chunks below. "
            "After every claim, cite the chunk number(s) like [1] or [1][3]. "
            "If the context does not contain the answer, say so. Be concise."
        )
        user_msg = "Context:\n" + numbered_context + "\n\nQuestion: " + question
        print("Prompt built (system + context + question). Calling Groq...")

        # STEP 6: Call Groq
        print("\n--- STEP 6: Call Groq ---")
        response = groq_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
            max_tokens=250,
        )
        answer = response.choices[0].message.content.strip()

        # STEP 7: Print answer + citations
        print("\n--- STEP 7: Answer + citations ---")
        print(f"  {answer}")

    # ==================================================================
    print_header("RECAP")
    print(
        "\n- LOAD + CHUNK: pull text from a PDF, cut at sentence boundaries.\n"
        "- EMBED + STORE: save vectors in Chroma (Lecture 2 pattern).\n"
        "- RETRIEVE: ask Chroma for the top chunks by meaning.\n"
        "- ANSWER: stuff top chunks into the prompt; cite sources like [1][2].\n"
        "- Whole loop is pure Python. Lecture 4 rebuilds this with LangChain."
    )


if __name__ == "__main__":
    main()
