import os
from openai import OpenAI
from dotenv import load_dotenv
from langdetect import detect

from store import retrieve_chunks

load_dotenv()

client = OpenAI(
    base_url="https://api.sarvam.ai/v1",
    api_key=os.environ.get("SARVAM_API_KEY"),
)
SARVAM_MODEL = "sarvam-105b-conversations"

LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "or": "Odia",
}


def build_prompt(query: str, chunks: list, lang_name: str) -> str:
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )
    return f"""You are a helpful assistant for NIT Rourkela students. Answer the student's question using ONLY the context below. If the context doesn't contain the answer, say you don't have that information — don't make anything up.

Answer in {lang_name}, the same language the question was asked in.

Context:
{context}

Question: {query}

Answer:"""


def answer_question(query: str) -> str:
    detected = detect(query)
    lang_name = LANG_NAMES.get(detected, "English")

    chunks = retrieve_chunks(query, n_results=3)
    if not chunks:
        return "I couldn't find any relevant information to answer that."

    prompt = build_prompt(query, chunks, lang_name)

    response = client.chat.completions.create(
        model=SARVAM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content
    if content is None:
        return "The model returned an empty response."
    return content


if __name__ == "__main__":
    print("=== English ===")
    print(answer_question("When is the mid semester examination?"))

    print("\n\n=== Hindi ===")
    print(answer_question("मध्य सेमेस्टर परीक्षा कब है"))