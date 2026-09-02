import time

import numpy as np

from db import get_all_documents
from tests.embeddings_demo import embed_texts, cosine_similarity


def get_top_chunks(query, k=3, source_filter=None):
    """Embed the query and return the top k most similar chunks (content, score, source).

    If source_filter is given, only search chunks whose source_name
    matches it.
    """
    documents = get_all_documents()
    if source_filter:
        documents = [doc for doc in documents if doc["source_name"] == source_filter]
    if not documents:
        return []

    embed_start = time.perf_counter()
    query_embedding = embed_texts([query])[0]
    embed_time = time.perf_counter() - embed_start

    search_start = time.perf_counter()
    scored = []
    for doc in documents:
        embedding = np.array(doc["embedding"])
        if embedding.shape != query_embedding.shape:
            continue
        score = cosine_similarity(query_embedding, embedding)
        scored.append((doc["content"], score, doc["source_name"]))

    scored.sort(key=lambda item: item[1], reverse=True)
    search_time = time.perf_counter() - search_start

    print(f"[timing] embed: {embed_time:.3f}s, retrieval: {search_time:.3f}s")

    return scored[:k]
