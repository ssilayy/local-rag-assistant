from retrieval import get_top_chunks

TEST_QUERIES = [
    "RAG sistemi nasıl çalışır?",
    "Cosine similarity nedir?",
    "SQLite nedir?",
]


def main():
    for query in TEST_QUERIES:
        print(f"Sorgu: {query}")
        results = get_top_chunks(query, k=3)
        for rank, (content, score, source_name) in enumerate(results, start=1):
            print(f"  [{rank}] (skor: {score:.4f}, kaynak: {source_name}) {content}")
        print()


if __name__ == "__main__":
    main()
