# demo_3_langchain_loaders_splitters.py
# Lecture 4 -- Demo 3: LangChain Documents, loaders, and splitters (survey)
#
# THE BIG IDEA
# -------------
# Before an end-to-end RAG chain, you need to know THREE basic building blocks:
#   1. Document  -- LangChain's unit of text (page_content + metadata)
#   2. Loaders   -- turn a file/URL into Document(s)
#   3. Splitters -- cut long Documents into smaller chunks
#
# This demo is a SURVEY: show the main kinds with tiny examples.
# Demo 4 wires them into a full RAG pipeline.
#
# DEVOPS ANALOGY
# --------------
# Loader  = "cat / path to the right file type" (pick the tool that matches the format)
# Splitter = "how you cut a long log before searching it"

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*langchain-community.*")

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEMOS_DIR = Path(__file__).resolve().parent
LECTURE4 = DEMOS_DIR.parent
SAMPLE_TXT = DEMOS_DIR / "sample_runbook_snippet.txt"
PDF_CANDIDATES = [
    LECTURE4 / "devops_runbook.pdf",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def part_1_what_is_a_document() -> None:
    print_header("PART 1: What is a Document?")
    print(
        """
  LangChain stores text as Document objects. Two fields matter today:

      page_content  -> the actual text string
      metadata      -> a small dict (source file, page number, tags, ...)

  Everything a loader returns is a list of Documents.
  Everything a splitter returns is also a list of Documents (smaller ones).
"""
    )
    doc = Document(
        page_content="If a pod shows OOMKilled, raise the memory limit.",
        metadata={"source": "manual", "topic": "k8s"},
    )
    print(f"  page_content: {doc.page_content!r}")
    print(f"  metadata:     {doc.metadata}")


def part_2_loaders() -> None:
    print_header("PART 2: Loaders -- pick the one that matches your file type")

    print(
        """
  Common beginner loaders (you will not run every one today):

    TextLoader / manual Document   -> .txt or a string you already have
    PyPDFLoader                    -> .pdf
    CSVLoader                      -> .csv tables
    WebBaseLoader / URL loaders    -> a web page
    JSONLoader                     -> .json
    DirectoryLoader                -> walk a folder and load many files

  Rule of thumb: match the loader to the format. Wrong loader = broken text.
"""
    )

    # --- Working example A: TextLoader on a tiny .txt ---
    print("\n--- Example A: TextLoader on sample_runbook_snippet.txt ---")
    if not SAMPLE_TXT.exists():
        print(f"  SKIP: missing {SAMPLE_TXT.name}")
    else:
        txt_docs = TextLoader(str(SAMPLE_TXT), encoding="utf-8").load()
        print(f"  Loaded {len(txt_docs)} Document(s) from TextLoader.")
        print(f"  First 120 chars: {txt_docs[0].page_content[:120]!r}...")
        print(f"  metadata: {txt_docs[0].metadata}")

    # --- Working example B: PyPDFLoader on the Lecture 3 runbook PDF ---
    print("\n--- Example B: PyPDFLoader on devops_runbook.pdf ---")
    pdf_path = next((p for p in PDF_CANDIDATES if p.exists()), None)
    if pdf_path is None:
        print("  SKIP: devops_runbook.pdf not found (expected under lecture3/).")
        print("  Tip: keep lecture3/devops_runbook.pdf next to this course tree.")
    else:
        pdf_docs = PyPDFLoader(str(pdf_path)).load()
        print(f"  Loaded {len(pdf_docs)} page Document(s) from {pdf_path.name}.")
        preview = pdf_docs[0].page_content.replace("\n", " ").strip()[:120]
        print(f"  Page 0 preview: {preview!r}...")
        print(f"  metadata keys: {sorted(pdf_docs[0].metadata.keys())}")


def part_3_splitters() -> None:
    print_header("PART 3: Splitters -- how you cut long text into chunks")

    print(
        """
  Main kinds for beginners:

    CharacterTextSplitter
        Cuts on a separator (often \"\\n\\n\" or \"\") with a fixed chunk_size.
        Simple idea: \"every N characters, cut.\"

    RecursiveCharacterTextSplitter   <-- default you will use most
        Tries paragraph breaks, then lines, then spaces -- keeps meaning together.
        Think: \"prefer cutting at natural boundaries.\"

    Token-based splitters (mention only)
        Exist when you must stay under a model token limit.
        Same idea as character splitters, counted in tokens instead of chars.
"""
    )

    # Multi-paragraph text so Recursive can cut on "\n\n" while Character
    # (separator="") cuts every N characters -- even mid-word.
    paragraph = (
        "OOMKilled means the kernel killed the container for using too much memory.\n\n"
        "Check the exit code and recent memory metrics first. "
        "Then raise the limit or find the leak.\n\n"
        "Escalate if the pod keeps restarting after the change."
    )

    char_splitter = CharacterTextSplitter(
        separator="",
        chunk_size=70,
        chunk_overlap=0,
    )
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=70,
        chunk_overlap=0,
    )

    char_chunks = char_splitter.split_text(paragraph)
    recursive_chunks = recursive_splitter.split_text(paragraph)

    print("\n--- Same text, both splitters (chunk_size=70) ---")
    print(f"\n  Input ({len(paragraph)} chars):")
    print(f"  {paragraph!r}")

    print(f"\n  CharacterTextSplitter (separator='') -> {len(char_chunks)} chunk(s):")
    for i, c in enumerate(char_chunks, 1):
        print(f"    [{i}] ({len(c)} chars) {c!r}")

    print(f"\n  RecursiveCharacterTextSplitter -> {len(recursive_chunks)} chunk(s):")
    for i, c in enumerate(recursive_chunks, 1):
        print(f"    [{i}] ({len(c)} chars) {c!r}")

    print(
        "\n  Look at the cuts: Character can slice mid-word.\n"
        "  Recursive prefers paragraph/line/space boundaries.\n"
        "  Recursive is the everyday default for RAG."
    )


def main() -> None:
    print()
    print("LECTURE 4 -- DEMO 3")
    print("LangChain survey: Document + loaders + splitters")
    print("=" * 70)

    part_1_what_is_a_document()
    part_2_loaders()
    part_3_splitters()

    print_header("RECAP")
    print(
        "\n- Document = page_content + metadata\n"
        "- Loader    = file/URL -> list[Document] (match the file type)\n"
        "- Splitter  = long text -> smaller Documents (prefer Recursive)\n"
        "- Next demo: Load -> Split -> Embed/Store -> Retrieve -> Prompt -> LLM\n"
        "  as one end-to-end LangChain RAG chain"
    )


if __name__ == "__main__":
    main()
