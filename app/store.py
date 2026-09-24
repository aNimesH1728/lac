import json
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

CHUNKS_FILE = "data/processed/chunks.json"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "college_docs"

MODEL_NAME = "intfloat/multilingual-e5-base"


def load_chunks() -> list:
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_vector_store():
    print(f"Loading embedding model: {MODEL_NAME} (first run downloads it, ~1GB)")
    model = SentenceTransformer(MODEL_NAME)

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks to embed")

    texts = ["passage: " + c["text"] for c in chunks]

    print("Embedding chunks (this takes a while on CPU, be patient)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[f"{c['source']}_{c['chunk_index']}" for c in chunks],
        embeddings=embeddings.tolist(),
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
    )

    print(f"Stored {collection.count()} chunks in ChromaDB at ./{CHROMA_DIR}")
    return collection


def retrieve_chunks(query: str, n_results: int = 3) -> list:
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    query_embedding = model.encode(["query: " + query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    docs = results.get("documents")
    metas = results.get("metadatas")
    dists = results.get("distances")

    if not docs or not metas or not dists:
        return []

    chunks = []
    for doc, meta, dist in zip(docs[0], metas[0], dists[0]):
        chunks.append({"text": doc, "source": meta["source"], "distance": dist})
    return chunks


def search(query: str, n_results: int = 3):
    chunks = retrieve_chunks(query, n_results)
    for i, c in enumerate(chunks):
        print(f"\n--- Result {i+1} (source: {c['source']}, distance: {c['distance']:.4f}) ---")
        print(c["text"][:300])


if __name__ == "__main__":
    build_vector_store()

    print("\n\n=== Test query (English) ===")
    search("when is the mid semester examination")

    print("\n\n=== Test query (Hindi) ===")
    search("मध्य सेमेस्टर परीक्षा कब है")