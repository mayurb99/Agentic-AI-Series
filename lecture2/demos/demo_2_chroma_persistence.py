# demo_2_chroma_persistence.py
# Lecture 2 -- Demo 2: In-memory vs. persistent vector stores
#
# THE BIG IDEA
# -------------
# Chroma (the vector database this lecture uses) can run in two modes:
#   1. In-memory  -- fast, lives only in RAM, gone the moment the process ends.
#   2. Persistent -- backed by real files on disk, survives a restart.
#
# DEVOPS ANALOGY -- container filesystem vs. mounted volume
# -------------------------------------------------------------
# A container's own filesystem disappears the instant the container restarts,
# unless you mount a volume. Chroma's in-memory mode is the bare-container
# case. Passing a persist_directory to Chroma is the mounted-volume case --
# the data is written to disk, so it's still there next time you start up.
#
# HOW TO SEE THE DIFFERENCE YOURSELF
# -------------------------------------
# Run this script twice in a row:
#   python demo_2_chroma_persistence.py
#   python demo_2_chroma_persistence.py
# On the first run, the persistent collection is created and populated.
# On the second run, the script finds the data already on disk from last
# time and skips re-adding it -- proof that it survived the process exiting.

import sys

import chromadb
from chromadb.utils import embedding_functions

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PERSIST_DIR = "./chroma_store_demo2"

SAMPLE_DOCS = [
    "The pod was killed by the OOM killer after exceeding its memory limit.",
    "The TLS certificate expired, causing every HTTPS request to fail.",
    "DNS resolution failed after the CoreDNS pods moved to a new node.",
    "A bad deployment was automatically rolled back after error rates spiked.",
    "The database connection pool was exhausted by a long-running query.",
]

# A local embedding model, wrapped so Chroma can call it automatically
# every time we add or query documents. Same model as demo 1.
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def demo_in_memory() -> None:
    print_header("PART 1: In-memory mode (chromadb.Client)")

    # No path given -- everything lives in RAM for this process only.
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name="devops_docs_memory", embedding_function=embedding_fn
    )

    collection.add(
        documents=SAMPLE_DOCS,
        ids=[f"mem_{i}" for i in range(len(SAMPLE_DOCS))],
    )
    print(f"Added {collection.count()} documents to an in-memory collection.")

    results = collection.query(query_texts=["the machine ran out of RAM"], n_results=1)
    print(f"Query 'the machine ran out of RAM' -> best match: \"{results['documents'][0][0]}\"")

    print(
        "\nThis collection exists ONLY inside this running Python process. "
        "The moment this script exits, it is gone -- exactly like writing a "
        "file inside a container with no volume mounted."
    )


def demo_persistent() -> None:
    print_header("PART 2: Persistent mode (chromadb.PersistentClient)")

    # This path is where Chroma writes its files to disk. Deleting this
    # folder is the equivalent of deleting a mounted volume.
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(
        name="devops_docs_persistent", embedding_function=embedding_fn
    )

    if collection.count() == 0:
        print(f"No existing data found in '{PERSIST_DIR}'. Adding documents for the first time.")
        collection.add(
            documents=SAMPLE_DOCS,
            ids=[f"disk_{i}" for i in range(len(SAMPLE_DOCS))],
        )
    else:
        print(
            f"Found {collection.count()} documents already on disk in "
            f"'{PERSIST_DIR}' -- this is data from a PREVIOUS run of this "
            "script. Nothing was re-added."
        )

    results = collection.query(query_texts=["the machine ran out of RAM"], n_results=1)
    print(f"Query 'the machine ran out of RAM' -> best match: \"{results['documents'][0][0]}\"")

    print(
        f"\nThis collection is backed by real files under '{PERSIST_DIR}'. "
        "Run this script again and it will find this same data waiting "
        "for it -- exactly like reattaching a mounted volume to a new container."
    )


def main() -> None:
    demo_in_memory()
    demo_persistent()

    print_header("RECAP")
    print(
        "\n- chromadb.Client()            -> in-memory, gone when the process exits.\n"
        "- chromadb.PersistentClient(path=...) -> backed by disk, survives restarts.\n"
        "- Same trade-off as an ephemeral container filesystem vs. a mounted\n"
        "  volume: pick persistent mode whenever the data needs to outlive\n"
        "  a single run.\n\n"
        f"Tip: delete the '{PERSIST_DIR}' folder if you want to reset this\n"
        "demo back to a first-run state."
    )


if __name__ == "__main__":
    main()
