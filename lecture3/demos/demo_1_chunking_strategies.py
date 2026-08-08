# demo_1_chunking_strategies.py
# Lecture 3 -- Demo 1: How do we cut a long document into chunks?
#
# THE BIG IDEA
# -------------
# Before you embed or search, you must cut a document into smaller pieces
# ("chunks"). This demo shows two common ways on the SAME runbook section.
#
# SIMPLE ANALOGIES
# ----------------
# Fixed-size      -> cut a long log every N characters, even mid-sentence
# Sentence-aware  -> cut at sentence boundaries so each piece still makes sense

import sys

from _chunking import fixed_size_chunks, sentence_aware_chunks
from _runbook_content import RUNBOOK_SECTIONS

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    print()
    print("LECTURE 3 -- DEMO 1")
    print("Chunking: Fixed-size vs. Sentence-aware")
    print("=" * 70)
    print(
        "\nSame runbook section, different cut styles. Read the cut points -- "
        "that is the whole lesson."
    )

    # Use Section 3 (OOM kills) -- long enough to need several chunks.
    section = RUNBOOK_SECTIONS[2]
    source_text = section["text"]
    print(f"\nSource: \"{section['title']}\"")
    print(f"Length: {len(source_text)} characters")

    # ------------------------------------------------------------------
    # PART 1: Fixed-size -- cut every 180 characters
    # ------------------------------------------------------------------
    print_header("PART 1: Fixed-size chunking -- cut every N characters")

    fixed_chunks = fixed_size_chunks(source_text, chunk_size=180)
    print(f"\nCut into {len(fixed_chunks)} chunks of up to 180 characters each:\n")

    for i, chunk in enumerate(fixed_chunks, start=1):
        # A rough clue that we cut mid-sentence: does not end with . ! or ?
        ends_clean = chunk[-1] in ".!?"
        flag = ""
        if not ends_clean:
            flag = "  <-- cuts mid-sentence"
        print(f"  [{i}] \"{chunk}\"{flag}")

    print(
        "\nNotice: at least one cut lands mid-sentence. "
        "The code only counts characters -- like slicing a long log file "
        "every N characters, even if that splits a line in half."
    )

    # ------------------------------------------------------------------
    # PART 2: Sentence-aware -- cut at . ! or ?
    # ------------------------------------------------------------------
    print_header("PART 2: Sentence-aware chunking -- cut at sentence boundaries")

    smart_chunks = sentence_aware_chunks(source_text, target_size=180)
    print("\nSame source, same ~180-character target, but respect sentences:\n")

    for i, chunk in enumerate(smart_chunks, start=1):
        print(f"  [{i}] ({len(chunk)} chars) \"{chunk}\"")

    print(
        "\nEvery chunk ends with '.', '!', or '?'. Sizes vary a little -- "
        "that is the trade: you give up exact length so each piece still "
        "reads as a complete thought."
    )

    # ------------------------------------------------------------------
    # RECAP
    # ------------------------------------------------------------------
    print_header("RECAP")
    print(
        "\n- Fixed-size: cut every N characters -- like slicing a log mid-line.\n"
        "- Sentence-aware: cut at sentence boundaries -- each piece still makes sense.\n"
        "- Next: once you have chunks, how do you SEARCH them well?"
    )


if __name__ == "__main__":
    main()
