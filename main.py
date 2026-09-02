from rag import answer_query


def main():
    """Ask questions until the user types 'exit'."""
    print("Local RAG Assistant started")
    print("Type your question (or 'exit' to quit):\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Bye.")
            break

        if not question:
            continue

        answer = answer_query(question)
        print(f"Answer: {answer}\n")


if __name__ == "__main__":
    main()
