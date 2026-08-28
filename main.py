from rag import answer_query


def main():
    """Kullanıcıdan konsoldan soru alıp 'exit' yazılana kadar cevap döndürür."""
    print("Local RAG Assistant başlatıldı")
    print("Sorunuzu yazın (çıkmak için 'exit'):\n")

    while True:
        question = input("Soru: ").strip()

        if question.lower() == "exit":
            print("Görüşürüz.")
            break

        if not question:
            continue

        answer = answer_query(question)
        print(f"Cevap: {answer}\n")


if __name__ == "__main__":
    main()
