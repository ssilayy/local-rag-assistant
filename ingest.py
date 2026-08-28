import time
from pathlib import Path

from db import init_db, insert_document, get_all_documents
from embeddings_demo import embed_texts

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def chunk_text(text):
    """Metni boş satırlara göre paragraf parçalarına böler."""
    paragraphs = [p.strip() for p in text.split("\n\n")]
    return [p for p in paragraphs if p]


def load_chunks():
    """documents/ altındaki .txt dosyalarını okuyup chunk/kaynak listesi döndürür."""
    chunks = []
    sources = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        for chunk in chunk_text(text):
            chunks.append(chunk)
            sources.append(path.name)
    return chunks, sources


def main():
    """Yeni chunk'ları embed edip veritabanına kaydeder; zaten işlenmişleri atlar."""
    init_db()

    chunks, sources = load_chunks()
    print(f"{len(chunks)} chunk bulundu.")

    # Aynı içerik + kaynak zaten embed edilip kaydedilmişse tekrar embed etme.
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
        print(f"{skipped} chunk zaten embed edilmiş, atlanıyor.")

    if new_pairs:
        new_chunks = [chunk for chunk, _ in new_pairs]
        new_sources = [source_name for _, source_name in new_pairs]

        print(f"{len(new_chunks)} yeni chunk embed ediliyor...")
        embed_start = time.perf_counter()
        embeddings = embed_texts(new_chunks)
        embed_time = time.perf_counter() - embed_start
        print(f"[timing] embed: {embed_time:.3f}s")

        for chunk, embedding, source_name in zip(new_chunks, embeddings, new_sources):
            insert_document(chunk, embedding.tolist(), source_name=source_name)
    else:
        print("Yeni chunk yok, embedding hesaplanmadı.")

    total = len(get_all_documents())
    print(f"Veritabanındaki toplam kayıt sayısı: {total}")


if __name__ == "__main__":
    main()
