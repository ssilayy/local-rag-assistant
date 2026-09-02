import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieval import get_top_chunks

TEST_QUERIES = [
    "How does a RAG system work?",
    "What is cosine similarity?",
    "What is SQLite?",
]


def main():
    for query in TEST_QUERIES:
        print(f"Query: {query}")
        results = get_top_chunks(query, k=3)
        for rank, (content, score, source_name) in enumerate(results, start=1):
            print(f"  [{rank}] (score: {score:.4f}, source: {source_name}) {content}")
        print()


if __name__ == "__main__":
    main()
