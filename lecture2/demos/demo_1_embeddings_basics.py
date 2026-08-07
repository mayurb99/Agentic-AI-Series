# demo_1_embeddings_basics.py
# Lecture 2 -- Demo 1: What is an embedding, really?
#
# THE BIG IDEA
# -------------
# An embedding turns a piece of text into a list of numbers (a "vector").
# The magic property: sentences with SIMILAR MEANING get numbers that are
# CLOSE TOGETHER, even if they don't share many of the same words.
#
# DEVOPS ANALOGY -- a fingerprint of meaning (contrast with a hash)
# -----------------------------------------------------------------
# You already know sha256sum / Docker image digests: change ONE character of
# the input and the hash comes out completely different. Hashes are designed
# so similar inputs do NOT look similar in the output.
#
# An embedding is a fingerprint too -- but built for the OPPOSITE job. Two
# sentences that mean almost the same thing should produce vectors that are
# close together, so a computer can search by MEANING instead of exact text.
#
# This demo proves both halves of that claim with real numbers.

import sys

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A small, fast model that runs on a laptop CPU in a couple of seconds.
# It downloads once (~80 MB) the first time you run this, then it's cached.
MODEL_NAME = "all-MiniLM-L6-v2"


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def part_1_what_does_a_vector_look_like(model: SentenceTransformer) -> None:
    print_header("PART 1: What does an embedding actually look like?")

    sentence = "The pod crashed due to an out-of-memory error."
    vector = model.encode(sentence)

    print(f"\nSentence: \"{sentence}\"")
    print(f"Embedding has {len(vector)} numbers (dimensions).")
    print(f"First 8 numbers: {[round(float(x), 3) for x in vector[:8]]}")
    print(
        "\nThat's it -- a sentence became a fixed-length list of floats. "
        "Every sentence you encode with this model produces exactly "
        f"{len(vector)} numbers, whether it's 3 words or 300."
    )


def part_2_similar_meaning_close_vectors(model: SentenceTransformer) -> None:
    print_header("PART 2: Similar meaning -> close vectors")

    pairs = [
        (
            "The pod crashed due to an out-of-memory error.",
            "The container was killed for using too much RAM.",
            "same meaning, almost no shared words",
        ),
        (
            "The pod crashed due to an out-of-memory error.",
            "The cafeteria serves lunch at noon.",
            "completely unrelated topics",
        ),
    ]

    for sentence_a, sentence_b, description in pairs:
        vec_a = model.encode(sentence_a)
        vec_b = model.encode(sentence_b)
        similarity = float(cos_sim(vec_a, vec_b)[0][0])

        print(f"\nA: \"{sentence_a}\"")
        print(f"B: \"{sentence_b}\"")
        print(f"({description})")
        print(f"Cosine similarity: {similarity:.4f}  (1.0 = identical meaning, 0.0 = unrelated)")

    print(
        "\nNotice: the first pair shares almost no words, but scores high. "
        "The second pair shares zero topic overlap and scores low. "
        "The model is comparing MEANING, not spelling."
    )


def part_3_hashes_do_the_opposite() -> None:
    print_header("PART 3: Contrast -- a hash destroys similarity on purpose")

    import hashlib

    sentence_a = "The pod crashed due to an out-of-memory error."
    sentence_b = "The pod crashed due to an out-of-memory error!"  # one char added

    hash_a = hashlib.sha256(sentence_a.encode()).hexdigest()
    hash_b = hashlib.sha256(sentence_b.encode()).hexdigest()

    print(f"\nA: \"{sentence_a}\"")
    print(f"B: \"{sentence_b}\"  (only one '!' added at the end)")
    print(f"\nSHA-256(A): {hash_a}")
    print(f"SHA-256(B): {hash_b}")
    print(
        "\nOne extra character and the hash is 100% different -- that's what "
        "checksums and image digests are for. An embedding of these two "
        "sentences, by contrast, would land almost on top of each other, "
        "because the MEANING barely changed."
    )


def main() -> None:
    print("Loading embedding model (first run downloads it, then it's cached)...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded: {MODEL_NAME}")

    part_1_what_does_a_vector_look_like(model)
    part_2_similar_meaning_close_vectors(model)
    part_3_hashes_do_the_opposite()

    print_header("RECAP")
    print(
        "\n- An embedding is a fixed-length vector of numbers representing meaning.\n"
        "- Similar meaning -> vectors close together (high cosine similarity).\n"
        "- A hash does the opposite on purpose: tiny input change -> totally\n"
        "  different output. Embeddings and hashes are both 'fingerprints',\n"
        "  built for opposite goals.\n"
        "- Next demo: where do we STORE thousands of these vectors so we can\n"
        "  search them later? That's what a vector database (Chroma) is for."
    )


if __name__ == "__main__":
    main()
