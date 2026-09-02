import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import answer_query

TEST_QUERIES_PATH = Path(__file__).parent / "test_queries.json"

REFUSAL_PHRASE = "don't have this information"


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

    header = f"{'#':<3} {'Question':<47} {'Expected':<14} {'Actual':<14} {'Result':<6}"
    print(header)
    print("-" * len(header))
    for i, r in enumerate(results, start=1):
        result_mark = "OK" if r["match"] else "FAIL"
        print(
            f"{i:<3} {truncate(r['question']):<47} {r['expected']:<14} "
            f"{r['actual']:<14} {result_mark:<6}"
        )

    print("\nDetailed answers:\n")
    for i, r in enumerate(results, start=1):
        print(f"[{i}] Question: {r['question']}")
        print(f"    Expected: {r['expected']} | Actual: {r['actual']}")
        print(f"    Answer: {r['answer']}")
        print()

    correct = sum(1 for r in results if r["match"])
    total = len(results)
    print(f"Summary: {correct}/{total} questions matched the expected behavior.")


if __name__ == "__main__":
    main()
