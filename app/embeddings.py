from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = "intfloat/multilingual-e5-base"

_model = None


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME} (first call this process)")
        _model = SentenceTransformer(MODEL_NAME)
    return _model