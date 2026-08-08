# _chunking.py
# Two small helpers that cut a long document into smaller pieces ("chunks").
# Demo 1 and Demo 3 both need this, so it lives in one place.

import re


def fixed_size_chunks(text, chunk_size=220):
    """Cut every N characters, even mid-sentence."""
    chunks = []
    start = 0
    while start < len(text):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(piece)
        start = start + chunk_size
    return chunks


def sentence_aware_chunks(text, target_size=220):
    """
    Group whole sentences until we near target_size.
    Never split a sentence in the middle.
    """
    # Replace newlines with spaces, then split after . ! or ?
    clean = text.replace("\n", " ").strip()
    sentences = re.split(r"(?<=[.!?])\s+", clean)

    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Would adding this sentence make the chunk too long?
        if current and len(current) + 1 + len(sentence) > target_size:
            chunks.append(current)
            current = sentence
        elif current:
            current = current + " " + sentence
        else:
            current = sentence

    if current:
        chunks.append(current)

    return chunks
