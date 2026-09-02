import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

SAMPLE_SENTENCES = [
    "The cat is sunbathing in the garden.",
    "Python is a popular programming language for data science.",
    "It will rain in Istanbul tomorrow.",
    "The central bank announced its interest rate decision.",
    "AI models can extract meaning from text.",
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
        lambda progress: print(f"\rDownloading model: {progress:.2f}%", end="", flush=True)
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
    print("Embedding sample sentences...")
    embeddings = embed_texts(SAMPLE_SENTENCES)
    print(f"Embedded {len(SAMPLE_SENTENCES)} sentences. Vector size: {embeddings.shape[1]}\n")

    query = "How does AI understand natural language?"
    print(f"Query: {query}")

    best_text, score = find_relevant(query, SAMPLE_SENTENCES)
    print(f"Most relevant sentence: {best_text}")
    print(f"Cosine similarity: {score:.4f}")


if __name__ == "__main__":
    main()
