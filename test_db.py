from db import init_db, insert_document, get_all_documents

SAMPLE_DOCUMENTS = [
    ("Kedi bahçede güneşleniyor.", [0.1, 0.2, 0.3]),
    ("Python veri bilimi için popüler bir dildir.", [0.4, 0.5, 0.6]),
    ("Yarın İstanbul'da hava yağmurlu olacak.", [0.7, 0.8, 0.9]),
    ("Yapay zeka modelleri metinden anlam çıkarabilir.", [0.15, 0.25, 0.35]),
]


def main():
    init_db()

    for content, embedding in SAMPLE_DOCUMENTS:
        insert_document(content, embedding)

    documents = get_all_documents()
    print(f"Toplam {len(documents)} döküman bulundu:\n")
    for doc in documents:
        print(f"id={doc['id']} content={doc['content']!r} embedding={doc['embedding']}")


if __name__ == "__main__":
    main()
