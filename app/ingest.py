import os
import json

from extractors import extract_text_from_file
from chunker import chunk_all_documents


RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
CHUNKS_FILE = os.path.join(PROCESSED_DIR, "chunks.json")


def load_all_documents() -> dict:
    documents = {}

    for filename in os.listdir(RAW_DIR):
        filepath = os.path.join(RAW_DIR, filename)

        text, method = extract_text_from_file(filepath, filename)

        if text is None:
            print(f"{filename}: extraction failed after all fallbacks — skipping")
            continue

        documents[filename] = text
        print(f"{filename}: {len(text)} chars, via {method} — preview: {text[:200]!r}")

    return documents


def save_chunks(chunks: list):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(chunks)} chunks to {CHUNKS_FILE}")


if __name__ == "__main__":
    docs = load_all_documents()
    chunks = chunk_all_documents(docs)
    print("\nSample chunk:")
    print(chunks[0])
    save_chunks(chunks)