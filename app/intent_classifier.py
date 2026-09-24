import csv
import joblib
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

load_dotenv()

DATA_FILE = "data/intents.csv"
MODEL_FILE = "app/intent_model.joblib"
EMBED_MODEL_NAME = "intfloat/multilingual-e5-base"  


def load_data():
    texts, labels = [], []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


def train():
    texts, labels = load_data()
    print(f"Loaded {len(texts)} labeled examples")

    embed_model = SentenceTransformer(EMBED_MODEL_NAME)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    print("Embedding training examples...")
    X_train_vec = embed_model.encode(["query: " + t for t in X_train], show_progress_bar=True)
    X_test_vec = embed_model.encode(["query: " + t for t in X_test], show_progress_bar=True)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train_vec, y_train)

    preds = clf.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    print(f"\nTest accuracy: {acc:.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, preds))

    joblib.dump({"classifier": clf}, MODEL_FILE)
    print(f"Saved model to {MODEL_FILE}")

    return embed_model, clf


def predict_intent(query: str, embed_model=None, clf=None) -> str:
    if embed_model is None or clf is None:
        embed_model = SentenceTransformer(EMBED_MODEL_NAME)
        bundle = joblib.load(MODEL_FILE)
        clf = bundle["classifier"]
    vec = embed_model.encode(["query: " + query])
    return clf.predict(vec)[0]


if __name__ == "__main__":
    embed_model, clf = train()

    print("\n=== Quick sanity checks ===")
    test_queries = [
        "When is the fee deadline?",
        "What's my attendance in Data Structures?",
        "I want to complain about the hostel mess",
        "मध्य सेमेस्टर परीक्षा की तारीख क्या है",
        "Someone is threatening me in my hostel",
        "What's the score of yesterday's IPL match?",
        "ମୋର ହଷ୍ଟେଲ ଫି ଦିଆ ହୋଇଛି କି?",
    ]
    for q in test_queries:
        pred = predict_intent(q, embed_model, clf)
        print(f"  {q!r} -> {pred}")