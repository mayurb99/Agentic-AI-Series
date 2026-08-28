# ingest.py
# Lecture 8 — Load data/ → chunk → embed → save to chroma_db/
#
# Run ONCE (or again after you change files under data/):
#   python ingest.py
#
# Same idea as Lecture 4 Demo 4:
#   TextLoader / PyPDFLoader → RecursiveCharacterTextSplitter
#   → HuggingFaceEmbeddings → Chroma (persist_directory)

from __future__ import annotations

import shutil
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*langchain-community.*")

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
CHROMA_DIR = HERE / "chroma_db"
COLLECTION_NAME = "oncall_runbooks"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# File types we load (.log treated as text)
TEXT_SUFFIXES = {".md", ".txt", ".log"}
PDF_SUFFIXES = {".pdf"}


def print_banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def load_documents():
    """Walk data/ and load md/txt/log/pdf into LangChain Documents."""
    docs = []
    files = sorted(p for p in DATA_DIR.rglob("*") if p.is_file())

    if not files:
        print(f"ERROR: no files found under {DATA_DIR}")
        sys.exit(1)

    for path in files:
        suffix = path.suffix.lower()
        rel = path.relative_to(HERE)

        if suffix in TEXT_SUFFIXES:
            loaded = TextLoader(str(path), encoding="utf-8").load()
        elif suffix in PDF_SUFFIXES:
            loaded = PyPDFLoader(str(path)).load()
        else:
            print(f"  skip (unsupported): {rel}")
            continue

        for d in loaded:
            d.metadata["source"] = str(rel).replace("\\", "/")
        docs.extend(loaded)
        print(f"  loaded: {rel} ({len(loaded)} doc(s))")

    return docs


def main() -> None:
    print()
    print("LECTURE 8 — ingest.py")
    print("On-call runbook helper: data/ -> Chroma")
    print("=" * 60)

    if not DATA_DIR.is_dir():
        print(f"ERROR: missing folder: {DATA_DIR}")
        sys.exit(1)

    # Wipe old DB so re-run is clean (idempotent rebuild)
    if CHROMA_DIR.exists():
        print_banner("STEP 0: Wipe old chroma_db/")
        shutil.rmtree(CHROMA_DIR)
        print(f"Removed {CHROMA_DIR}")

    print_banner("STEP 1: Load documents from data/")
    docs = load_documents()
    print(f"\nTotal documents loaded: {len(docs)}")

    print_banner("STEP 2: Split (RecursiveCharacterTextSplitter)")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"Chunks: {len(chunks)} (size=500, overlap=50)")

    print_banner("STEP 3: Embed + persist Chroma")
    print(f"Model: {EMBED_MODEL}")
    print("(First run may download ~80 MB, then cached.)")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME,
    )

    print_banner("SUCCESS")
    print(f"  docs   : {len(docs)}")
    print(f"  chunks : {len(chunks)}")
    print(f"  path   : {CHROMA_DIR}")
    print(f"  name   : {COLLECTION_NAME}")
    print("\nNext:  streamlit run app.py")


if __name__ == "__main__":
    main()
