import time
from pathlib import Path

from pypdf import PdfReader

from db import init_db, insert_document, get_all_documents
from tests.embeddings_demo import embed_texts

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def chunk_text(text):
    """Split text into paragraph chunks on blank lines."""
    paragraphs = [p.strip() for p in text.split("\n\n")]
    return [p for p in paragraphs if p]


def extract_pdf_text_by_page(path):
    """Extract text from a PDF, page by page."""
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return pages


def load_pdf_chunks(path):
    """Read a PDF page by page and split each page into paragraphs."""
    chunks = []
    for page_text in extract_pdf_text_by_page(path):
        chunks.extend(chunk_text(page_text))
    return chunks


def load_chunks():
    """Read the .txt and .pdf files under documents/ and return their chunks and sources."""
    chunks = []
    sources = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        for chunk in chunk_text(text):
            chunks.append(chunk)
            sources.append(path.name)
    for path in sorted(DOCUMENTS_DIR.glob("*.pdf")):
        for chunk in load_pdf_chunks(path):
            chunks.append(chunk)
            sources.append(path.name)
    return chunks, sources


def main():
    """Embed new chunks and save them to the database; skip ones already processed."""
    init_db()

    chunks, sources = load_chunks()
    print(f"Found {len(chunks)} chunks.")

    # Skip chunks that are already embedded and saved for the same source.
    already_embedded = {
        (doc["content"], doc["source_name"]) for doc in get_all_documents()
    }
    new_pairs = [
        (chunk, source_name)
        for chunk, source_name in zip(chunks, sources)
        if (chunk, source_name) not in already_embedded
    ]

    skipped = len(chunks) - len(new_pairs)
    if skipped:
        print(f"{skipped} chunks already embedded, skipping.")

    if new_pairs:
        new_chunks = [chunk for chunk, _ in new_pairs]
        new_sources = [source_name for _, source_name in new_pairs]

        print(f"Embedding {len(new_chunks)} new chunks...")
        embed_start = time.perf_counter()
        embeddings = embed_texts(new_chunks)
        embed_time = time.perf_counter() - embed_start
        print(f"[timing] embed: {embed_time:.3f}s")

        for chunk, embedding, source_name in zip(new_chunks, embeddings, new_sources):
            insert_document(chunk, embedding.tolist(), source_name=source_name)
    else:
        print("No new chunks, nothing to embed.")

    total = len(get_all_documents())
    print(f"Total records in database: {total}")


if __name__ == "__main__":
    main()
