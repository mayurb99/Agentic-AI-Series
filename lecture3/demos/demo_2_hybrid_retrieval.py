# demo_2_hybrid_retrieval.py
# Lecture 3 -- Demo 2: Keyword search + meaning search, used together
#
# THE BIG IDEA
# -------------
# Lecture 2 taught meaning search (embeddings). Keyword search still matters:
# exact error codes and rare terms. Hybrid = run BOTH, then combine scores.
#
# SIMPLE ANALOGY
# --------------
# Hybrid search = keyword search (grep) + meaning search (from L2), together.
#   BM25 (keyword)  -> great when the exact words match
#   Dense (meaning) -> great when the wording is different but the idea matches
#   Hybrid          -> give points for each method's top picks, pick highest total

import sys

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from _chunking import sentence_aware_chunks
from _runbook_content import RUNBOOK_SECTIONS

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL_NAME = "all-MiniLM-L6-v2"

# Simple points for being near the top of a ranking:
# 1st place = 3 points, 2nd = 2, 3rd = 1. Everyone else = 0.
TOP_POINTS = [3, 2, 1]


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def build_chunk_corpus():
    """Cut every runbook section into sentence-aware chunks."""
    corpus = []
    for section in RUNBOOK_SECTIONS:
        chunks = sentence_aware_chunks(section["text"], target_size=200)
        for i, chunk in enumerate(chunks):
            corpus.append(
                {
                    "id": section["id"] + "_chunk_" + str(i),
                    "section_title": section["title"],
                    "text": chunk,
                }
            )
    return corpus


def top3_indexes(scores):
    """Return the indexes of the 3 highest scores (best first)."""
    # Pair each score with its index, then sort high-to-low.
    paired = []
    for i, score in enumerate(scores):
        paired.append((score, i))
    paired.sort(reverse=True)

    indexes = []
    for rank in range(3):
        indexes.append(paired[rank][1])
    return indexes


def points_from_ranking(top_indexes, n_docs):
    """
    Turn a top-3 ranking into a points list.
    Example: if top_indexes = [5, 2, 9], then doc 5 gets 3, doc 2 gets 2,
    doc 9 gets 1, and every other doc gets 0.
    """
    points = [0] * n_docs
    for rank, doc_index in enumerate(top_indexes):
        points[doc_index] = TOP_POINTS[rank]
    return points


def best_index(scores):
    """Return the index of the highest score."""
    best_i = 0
    best_score = scores[0]
    for i, score in enumerate(scores):
        if score > best_score:
            best_score = score
            best_i = i
    return best_i


def run_query(query, corpus, bm25, model, corpus_embeddings):
    """
    Rank the same chunks three ways:
      1) keyword only (BM25)
      2) meaning only (embeddings)
      3) hybrid = keyword points + meaning points
    """
    n = len(corpus)

    # --- Keyword scores (BM25) ---
    query_words = query.lower().split()
    bm25_scores = list(bm25.get_scores(query_words))
    bm25_top = top3_indexes(bm25_scores)
    bm25_points = points_from_ranking(bm25_top, n)

    # --- Meaning scores (cosine similarity) ---
    query_vec = model.encode(query)
    dense_scores = []
    for doc_vec in corpus_embeddings:
        sim = float(cos_sim(query_vec, doc_vec)[0][0])
        dense_scores.append(sim)
    dense_top = top3_indexes(dense_scores)
    dense_points = points_from_ranking(dense_top, n)

    # --- Hybrid: just ADD the points ---
    # Plain English: "3 points if BM25 ranked it #1, 2 if #2, 1 if #3;
    # same for meaning search; highest total wins."
    hybrid_points = []
    for i in range(n):
        hybrid_points.append(bm25_points[i] + dense_points[i])

    bm25_winner = best_index(bm25_scores)
    dense_winner = best_index(dense_scores)
    hybrid_winner = best_index(hybrid_points)

    print(f"\nQuery: \"{query}\"")
    print()
    print("  Keyword (BM25) top 3:")
    for rank, i in enumerate(bm25_top):
        print(
            f"    #{rank + 1} (+{TOP_POINTS[rank]} pt) "
            f"[{corpus[i]['section_title']}] "
            f"\"{corpus[i]['text'][:70]}...\""
        )

    print("  Meaning (dense) top 3:")
    for rank, i in enumerate(dense_top):
        print(
            f"    #{rank + 1} (+{TOP_POINTS[rank]} pt) "
            f"[{corpus[i]['section_title']}] "
            f"\"{corpus[i]['text'][:70]}...\""
        )

    print()
    print(
        f"  Keyword winner -> [{corpus[bm25_winner]['section_title']}] "
        f"\"{corpus[bm25_winner]['text'][:80]}...\""
    )
    print(
        f"  Meaning winner -> [{corpus[dense_winner]['section_title']}] "
        f"\"{corpus[dense_winner]['text'][:80]}...\""
    )
    print(
        f"  Hybrid winner  -> [{corpus[hybrid_winner]['section_title']}] "
        f"(points={hybrid_points[hybrid_winner]}) "
        f"\"{corpus[hybrid_winner]['text'][:80]}...\""
    )


def main():
    print()
    print("LECTURE 3 -- DEMO 2")
    print("Hybrid retrieval: keyword (BM25) + meaning (embeddings)")
    print("=" * 70)
    print(
        "\nSame chunks, three ways to rank them: keyword only, meaning only, "
        "and both together (hybrid)."
    )
    print(
        "Hybrid math (keep it simple):\n"
        "  - Look at each method's top 3.\n"
        "  - Give 3 / 2 / 1 points for 1st / 2nd / 3rd.\n"
        "  - Add the points. Highest total wins."
    )

    # Build one corpus of chunks from the whole runbook.
    corpus = build_chunk_corpus()
    print(f"\nCorpus: {len(corpus)} chunks across {len(RUNBOOK_SECTIONS)} sections.")

    print("\nBuilding keyword index (BM25)...")
    tokenized = []
    for doc in corpus:
        tokenized.append(doc["text"].lower().split())
    bm25 = BM25Okapi(tokenized)

    print("Loading embedding model and encoding every chunk (meaning index)...")
    model = SentenceTransformer(MODEL_NAME)
    texts = []
    for doc in corpus:
        texts.append(doc["text"])
    corpus_embeddings = model.encode(texts)

    # ------------------------------------------------------------------
    print_header("PART 1: Exact keywords help -- BM25's strength")
    run_query(
        "OOMKilled exit code 137",
        corpus, bm25, model, corpus_embeddings,
    )
    print(
        "\nThis query reuses rare exact terms from the runbook ('OOMKilled', "
        "'137'). Keyword search locks onto those words."
    )

    # ------------------------------------------------------------------
    print_header("PART 2: Different wording -- meaning search's strength")
    run_query(
        "requests to our API suddenly all fail with a handshake error",
        corpus, bm25, model, corpus_embeddings,
    )
    print(
        "\nThis paraphrases the TLS certificate section with almost no shared "
        "words. Meaning search finds it; keyword search has little to grab. "
        "Hybrid should follow the meaning signal here."
    )

    # ------------------------------------------------------------------
    print_header("PART 3: Both signals agree -- hybrid combines them")
    run_query(
        "connection pool exhausted, queries timing out waiting for a connection",
        corpus, bm25, model, corpus_embeddings,
    )
    print(
        "\nThis query shares exact terms AND paraphrases the rest. Hybrid "
        "adds points from both rankings -- two votes beat one."
    )

    # ------------------------------------------------------------------
    print_header("RECAP")
    print(
        "\n- Keyword (BM25): like grep -- strong on exact words, weak on rewording.\n"
        "- Meaning (dense): like Lecture 2 search -- strong on ideas, weaker on rare codes.\n"
        "- Hybrid: give points to each method's top picks, add them up.\n"
        "- Next demo: full RAG loop on a PDF -- retrieve, then ask the LLM, with sources."
    )


if __name__ == "__main__":
    main()
