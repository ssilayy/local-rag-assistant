import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import init_db, insert_document, get_all_documents

SAMPLE_DOCUMENTS = [
    ("The cat is sunbathing in the garden.", [0.1, 0.2, 0.3]),
    ("Python is a popular language for data science.", [0.4, 0.5, 0.6]),
    ("It will rain in Istanbul tomorrow.", [0.7, 0.8, 0.9]),
    ("AI models can extract meaning from text.", [0.15, 0.25, 0.35]),
]


def main():
    init_db()

    for content, embedding in SAMPLE_DOCUMENTS:
        insert_document(content, embedding)

    documents = get_all_documents()
    print(f"Found {len(documents)} documents total:\n")
    for doc in documents:
        print(f"id={doc['id']} content={doc['content']!r} embedding={doc['embedding']}")


if __name__ == "__main__":
    main()
