import os

from extractors import extract_text_from_file
from chunker import chunk_all_documents


RAW_DIR = "data/raw"


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


if __name__ == "__main__":
    docs = load_all_documents()
    chunks = chunk_all_documents(docs)
    print("\nSample chunk:")
    print(chunks[0])