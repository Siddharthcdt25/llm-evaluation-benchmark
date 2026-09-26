import json


# Load evaluation results
with open("results.json", "r", encoding="utf-8") as file:
    results = json.load(file)


# --------------------------------------------------
# Overall Metrics
# --------------------------------------------------

total_tests = len(results)

passed = sum(
    1 for result in results
    if result["result"] == "PASS"
)

failed = sum(
    1 for result in results
    if result["result"] == "FAIL"
)

errors = sum(
    1 for result in results
    if result["result"] == "ERROR"
)


valid_results = [
    result["score"]
    for result in results
    if result["score"] is not None
]

overall_score = (
    sum(valid_results) / len(valid_results)
    if valid_results
    else 0
)


# --------------------------------------------------
# Category-Level Metrics
# --------------------------------------------------

categories = {}

for result in results:

    category = result["category"]

    if category not in categories:
        categories[category] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "scores": []
        }

    categories[category]["total"] += 1

    if result["result"] == "PASS":
        categories[category]["passed"] += 1

    elif result["result"] == "FAIL":
        categories[category]["failed"] += 1

    if result["score"] is not None:
        categories[category]["scores"].append(result["score"])


# --------------------------------------------------
# Display Overall Metrics
# --------------------------------------------------

print("=" * 60)
print("BENCHMARK METRICS")
print("=" * 60)

print(f"\nTotal tests : {total_tests}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Errors      : {errors}")

print(f"\nOverall score: {overall_score:.2%}")


# --------------------------------------------------
# Display Category Metrics
# --------------------------------------------------

print("\n" + "=" * 60)
print("CATEGORY METRICS")
print("=" * 60)

for category, data in categories.items():

    category_score = (
        sum(data["scores"]) / len(data["scores"])
        if data["scores"]
        else 0
    )

    print(f"\nCategory: {category}")
    print(f"Tests   : {data['total']}")
    print(f"Passed  : {data['passed']}")
    print(f"Failed  : {data['failed']}")
    print(f"Score   : {category_score:.2%}")