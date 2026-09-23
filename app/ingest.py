import os
import pdfplumber
import pytesseract
from pypdf import PdfReader
from bs4 import BeautifulSoup
from pdf2image import convert_from_path


RAW_DIR = "data/raw"


def is_garbled(text: str) -> bool:
    if len(text.strip()) < 50:
        return True
    control_chars = sum(1 for c in text if ord(c) < 32 and c not in "\n\t")
    if (control_chars / max(len(text), 1)) > 0.1:
        return True
    if text.count("(cid:") > 5:
        return True
    return False


def extract_text_pdfplumber(filepath: str) -> str:
    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_ocr(filepath: str) -> str:
    images = convert_from_path(filepath)
    text_parts = []
    for img in images:
        text_parts.append(pytesseract.image_to_string(img))
    return "\n".join(text_parts)


def extract_text_from_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text())
    return "\n".join(pages_text)


def extract_text_from_html(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for tag in soup(["nav", "footer", "script", "style", "header"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def load_all_documents() -> dict:
    documents = {}

    for filename in os.listdir(RAW_DIR):
        filepath = os.path.join(RAW_DIR, filename)

        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(filepath)
            method = "pypdf"

            if is_garbled(text):
                text = extract_text_pdfplumber(filepath)
                method = "pdfplumber"

            if is_garbled(text):
                text = extract_text_ocr(filepath)
                method = "ocr"

        elif filename.endswith(".html"):
            text = extract_text_from_html(filepath)
            method = "beautifulsoup"

        else:
            continue 

        if is_garbled(text):
            print(f"{filename}: still garbled/empty after all fallbacks ({len(text.strip())} chars) — skipping")
            continue

        documents[filename] = text
        print(f"{filename}: {len(text)} chars, via {method} — preview: {text[:200]!r}")

    return documents


if __name__ == "__main__":
    load_all_documents()