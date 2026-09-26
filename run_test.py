import json

from evaluation_engine import evaluate_test
from ollama_model_client import ask_ollama
# Load benchmark
with open("data/benchmark.json", "r", encoding="utf-8") as file:
    benchmark = json.load(file)

# TEMPORARY: run only the first benchmark test


print("=" * 60)
print("MULTI-TEST MODEL BENCHMARK")
print("=" * 60)

results = []

# Model mode
mode = "ollama"


# Run every benchmark test
for test in benchmark:

    print("\n" + "=" * 60)
    print(f"Test ID: {test['id']}")
    print(f"Category: {test['category']}")
    print(f"Evaluation Type: {test['evaluation_type']}")

    print("\nQuestion:")
    print(test["question"])

    print("\nModel response:")

    # Generate model response
    if mode == "ollama":

        model_response = ask_ollama(
            test["question"]
        )

    answer = model_response["answer"]

    # Handle model error
    if answer is None:

        print("ERROR: No model response available.")

        result = {
            "id": test["id"],
            "category": test["category"],
            "difficulty": test["difficulty"],
            "evaluation_type": test["evaluation_type"],
            "question": test["question"],
            "expected_answer": test["expected_answer"],
            "model_response": None,
            "model": "llama3.2:3b",
            "result": "ERROR",
            "score": None
        }

        results.append(result)
        continue

    print("-" * 60)
    print(answer)
    print("-" * 60)

    # Evaluate response
    evaluation = evaluate_test(test, answer)

    # Store result
    result = {
        "id": test["id"],
        "category": test["category"],
        "difficulty": test["difficulty"],
        "evaluation_type": test["evaluation_type"],
        "question": test["question"],
        "expected_answer": test["expected_answer"],
        "model_response": answer,
        "model": "llama3.2:3b",
        "result": evaluation.get("result"),
        "score": evaluation.get("score")
    }

    results.append(result)

    print("\nEvaluation:")
    print("-" * 60)
    print(f"Score: {evaluation.get('score')}")
    print(f"Result: {evaluation.get('result')}")


# Final summary
print("\n" + "=" * 60)
print("BENCHMARK SUMMARY")
print("=" * 60)

for result in results:
    print(
        f"{result['id']}: "
        f"{result['result']} "
        f"(Score: {result['score']})"
    )


# Save results to JSON
with open("results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\nResults saved to results.json")