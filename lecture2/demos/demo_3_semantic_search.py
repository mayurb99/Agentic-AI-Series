# demo_3_semantic_search.py
# Lecture 2 -- Demo 3: Semantic search over 50 documents
#
# THE BIG IDEA
# -------------
# We store 50 short DevOps "runbook" entries in a persistent Chroma
# collection, then search them by MEANING instead of by exact keyword.
#
# DEVOPS ANALOGY -- searching logs by meaning, not exact keywords
# --------------------------------------------------------------
# Keyword search (grep / Ctrl+F) needs the exact words. A vector database
# is a special search index for one job: "find the K closest meanings."
# You could store number lists in a normal table; Chroma exists because
# that one search pattern is specialized -- and that's what this demo shows.
#
# This demo has 2 parts:
#   1. Build the persistent collection (once).
#   2. Compare semantic search vs. naive keyword search on the same queries.

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


def compare_semantic_vs_keyword(collection: "chromadb.Collection") -> None:
    print_header("PART 2: Semantic search vs. naive keyword search")

    queries = [
        "the machine ran out of RAM",
        "a crash in the new code triggered the platform to restore the last known good release by itself",
        "encrypted connections to our api began failing right after midnight",
    ]

    for query in queries:
        semantic_results = collection.query(query_texts=[query], n_results=1)
        semantic_match = semantic_results["documents"][0][0]
        distance = semantic_results["distances"][0][0]

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


def main() -> None:
    print_header("PART 1: Build (or load) the 50-document knowledge base")
    collection = build_or_load_collection()

    compare_semantic_vs_keyword(collection)

    print_header("RECAP")
    print(
        "\n- 50 short documents were embedded once and stored persistently in Chroma.\n"
        "- Semantic search matched queries by meaning, even with zero shared\n"
        "  keywords -- naive keyword search often failed on the same queries.\n"
        "- That contrast is the whole point of this lecture: search by meaning,\n"
        "  not by exact spelling. Lecture 3 builds on this with RAG."
    )


if __name__ == "__main__":
    main()
