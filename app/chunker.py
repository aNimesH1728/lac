def chunk_text(text: str, source: str, chunk_size: int = 400, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    step = chunk_size - overlap 

    start = 0
    chunk_index = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_str = " ".join(chunk_words)

        chunks.append({
            "text": chunk_str,
            "source": source,
            "chunk_index": chunk_index,
        })

        chunk_index += 1
        start += step 

    return chunks


def chunk_all_documents(documents: dict) -> list:
    all_chunks = []
    for filename, text in documents.items():
        doc_chunks = chunk_text(text, source=filename)
        all_chunks.extend(doc_chunks)
        print(f"{filename}: {len(doc_chunks)} chunks")
    print(f"\nTotal chunks across all documents: {len(all_chunks)}")
    return all_chunks