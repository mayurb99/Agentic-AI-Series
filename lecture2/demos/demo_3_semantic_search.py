# demo_3_semantic_search.py
# Lecture 2 -- Demo 3: Semantic search over 50 documents
#
# THE BIG IDEA
# -------------
# We store 50 short DevOps "runbook" entries in a persistent Chroma
# collection, then search them by MEANING instead of by exact keyword.
#
# DEVOPS ANALOGY -- Prometheus/Elasticsearch vs. a general-purpose DB
# ------------------------------------------------------------------
# You could store metrics in Postgres, but you use Prometheus because it's
# purpose-built for one query pattern (time-range aggregation) and is far
# faster at it. Chroma is the same trade for a different query pattern:
# "find the K most similar vectors." That's the whole reason a vector
# database exists instead of just using arrays in a normal table.
#
# This demo has 3 parts:
#   1. Build the persistent collection (once).
#   2. Compare semantic search vs. naive keyword search on the same queries.
#   3. BONUS: feed the top search result to an LLM and get a plain-English
#      answer -- a two-line preview of what Lecture 3 (RAG) builds in full.

import sys

import chromadb
from chromadb.utils import embedding_functions

from _devops_corpus import DEVOPS_DOCS

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PERSIST_DIR = "./chroma_store_demo3"
COLLECTION_NAME = "devops_knowledge_base"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def build_or_load_collection() -> "chromadb.Collection":
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_fn
    )

    if collection.count() == 0:
        print(f"Embedding and storing {len(DEVOPS_DOCS)} documents (first run)...")
        collection.add(
            documents=[doc["text"] for doc in DEVOPS_DOCS],
            ids=[doc["id"] for doc in DEVOPS_DOCS],
        )
    else:
        print(f"Loaded {collection.count()} documents already stored in '{PERSIST_DIR}'.")

    return collection


def naive_keyword_search(query: str, top_k: int = 1) -> list[str]:
    """
    The 'before' picture: score each document by how many query words
    literally appear in it. No understanding of meaning at all.
    """
    query_words = set(query.lower().split())
    scored = []
    for doc in DEVOPS_DOCS:
        doc_words = set(doc["text"].lower().replace(".", "").split())
        overlap = len(query_words & doc_words)
        scored.append((overlap, doc["text"]))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [text for score, text in scored[:top_k] if score > 0] or ["(no keyword overlap found)"]


def compare_semantic_vs_keyword(collection: "chromadb.Collection") -> str:
    print_header("PART 2: Semantic search vs. naive keyword search")

    queries = [
        "the machine ran out of RAM",
        "a crash in the new code triggered the platform to restore the last known good release by itself",
        "encrypted connections to our api began failing right after midnight",
    ]

    last_semantic_result = ""

    for query in queries:
        semantic_results = collection.query(query_texts=[query], n_results=1)
        semantic_match = semantic_results["documents"][0][0]
        distance = semantic_results["distances"][0][0]
        last_semantic_result = semantic_match

        keyword_match = naive_keyword_search(query)[0]

        print(f"\nQuery: \"{query}\"")
        print(f"  Semantic search (Chroma)  -> \"{semantic_match}\" (distance={distance:.4f})")
        print(f"  Naive keyword search      -> \"{keyword_match}\"")

    print(
        "\nNotice: none of these queries reuse the document's exact wording "
        "('RAM' vs. 'memory', 'restore the last known good release' vs. "
        "'rolled back', 'encrypted connections... failing' vs. 'TLS "
        "certificate expired'). Semantic search still finds the right "
        "entry because it compares MEANING; keyword search latches onto "
        "whichever document happens to share the most common words -- "
        "usually the wrong one."
    )

    return last_semantic_result


def bonus_rag_preview(context_doc: str) -> None:
    print_header("BONUS PREVIEW: This + an LLM call is what Lecture 3 (RAG) does")

    import os

    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print(
            "\n(Skipped -- no GROQ_API_KEY configured. Demos 1 and 2, and "
            "everything above in this demo, work without one. This bonus "
            "section just previews what comes next.)"
        )
        return

    from _client import DEFAULT_MODEL, get_client

    question = "Why did our certificate-related outage happen, and how do we stop it recurring?"
    client = get_client()

    print(f"\nRetrieved context (from semantic search above):\n  \"{context_doc}\"")
    print(f"\nQuestion: \"{question}\"")

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using ONLY the provided context. "
                    "Be concise -- 2 sentences max."
                ),
            },
            {
                "role": "user",
                "content": f"Context: {context_doc}\n\nQuestion: {question}",
            },
        ],
    )
    print(f"\nLLM answer:\n  {response.choices[0].message.content}")
    print(
        "\nThat's the whole idea of RAG in miniature: retrieve the relevant "
        "chunk with a vector database, then hand it to an LLM as context. "
        "Lecture 3 builds this into a full pipeline."
    )


def main() -> None:
    print_header("PART 1: Build (or load) the 50-document knowledge base")
    collection = build_or_load_collection()

    last_result = compare_semantic_vs_keyword(collection)
    bonus_rag_preview(last_result)

    print_header("RECAP")
    print(
        "\n- 50 short documents were embedded once and stored persistently in Chroma.\n"
        "- Semantic search matched queries by meaning, even with zero shared\n"
        "  keywords -- naive keyword search often failed on the same queries.\n"
        "- Retrieved context + an LLM call = the core loop of RAG, which is\n"
        "  exactly what Lecture 3 builds out fully."
    )


if __name__ == "__main__":
    main()
