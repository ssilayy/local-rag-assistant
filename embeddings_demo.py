import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

SAMPLE_SENTENCES = [
    "Kedi bahçede güneşleniyor.",
    "Python, veri bilimi için popüler bir programlama dilidir.",
    "Yarın İstanbul'da hava yağmurlu olacak.",
    "Merkez bankası faiz kararını açıkladı.",
    "Yapay zeka modelleri metinden anlam çıkarabilir.",
]

_embedding_client = None


def _get_embedding_client():
    global _embedding_client
    if _embedding_client is not None:
        return _embedding_client

    if FoundryLocalManager.instance is None:
        config = Configuration(app_name="local_rag_assistant")
        FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model(EMBEDDING_MODEL_ALIAS)
    model.download(
        lambda progress: print(f"\rModel indiriliyor: {progress:.2f}%", end="", flush=True)
    )
    print()
    model.load()

    _embedding_client = model.get_embedding_client()
    return _embedding_client


def embed_texts(texts):
    client = _get_embedding_client()
    response = client.generate_embeddings(texts)
    return np.array([data.embedding for data in response.data])


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_relevant(query, texts):
    query_embedding = embed_texts([query])[0]
    text_embeddings = embed_texts(texts)

    similarities = [cosine_similarity(query_embedding, emb) for emb in text_embeddings]
    best_index = int(np.argmax(similarities))

    return texts[best_index], similarities[best_index]


def main():
    print("Örnek cümleler embed ediliyor...")
    embeddings = embed_texts(SAMPLE_SENTENCES)
    print(f"{len(SAMPLE_SENTENCES)} cümle embed edildi. Vektör boyutu: {embeddings.shape[1]}\n")

    query = "Yapay zeka doğal dili nasıl anlar?"
    print(f"Sorgu: {query}")

    best_text, score = find_relevant(query, SAMPLE_SENTENCES)
    print(f"En alakalı cümle: {best_text}")
    print(f"Cosine similarity: {score:.4f}")


if __name__ == "__main__":
    main()
