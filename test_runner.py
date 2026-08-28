import json
from pathlib import Path

from rag import answer_query

TEST_QUERIES_PATH = Path(__file__).parent / "test_queries.json"

REFUSAL_PHRASE = "elimde yok"


def classify_answer(answer):
    return "unanswerable" if REFUSAL_PHRASE in answer.lower() else "answerable"


def truncate(text, length=45):
    text = text.replace("\n", " ")
    return text if len(text) <= length else text[: length - 1] + "…"


def main():
    test_cases = json.loads(TEST_QUERIES_PATH.read_text(encoding="utf-8"))

    results = []
    for case in test_cases:
        question = case["question"]
        expected = case["expected_behavior"]
        answer = answer_query(question)
        actual = classify_answer(answer)
        results.append(
            {
                "question": question,
                "expected": expected,
                "actual": actual,
                "match": expected == actual,
                "answer": answer,
            }
        )

    header = f"{'#':<3} {'Soru':<47} {'Beklenen':<14} {'Gerçekleşen':<14} {'Sonuç':<6}"
    print(header)
    print("-" * len(header))
    for i, r in enumerate(results, start=1):
        result_mark = "OK" if r["match"] else "FAIL"
        print(
            f"{i:<3} {truncate(r['question']):<47} {r['expected']:<14} "
            f"{r['actual']:<14} {result_mark:<6}"
        )

    print("\nDetaylı cevaplar:\n")
    for i, r in enumerate(results, start=1):
        print(f"[{i}] Soru: {r['question']}")
        print(f"    Beklenen: {r['expected']} | Gerçekleşen: {r['actual']}")
        print(f"    Cevap: {r['answer']}")
        print()

    correct = sum(1 for r in results if r["match"])
    total = len(results)
    print(f"Özet: {correct}/{total} soru beklenen davranışa uydu.")


if __name__ == "__main__":
    main()
