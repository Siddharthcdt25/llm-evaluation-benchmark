def evaluate_reasoning_006(answer):

    answer_lower = answer.lower()

    correct_mapping = [
        (
            "apples and oranges",
            ["only apples", "apples only"]
        ),
        (
            "apples",
            ["only oranges", "oranges only"]
        ),
        (
            "oranges",
            ["both apples and oranges", "apples and oranges"]
        )
    ]

    checks = {}

    for label, valid_contents in correct_mapping:

        checks[label] = False

        for contents in valid_contents:

            if label in answer_lower and contents in answer_lower:
                checks[label] = True
                break

    passed = sum(checks.values())
    total = len(checks)

    score = passed / total

    return {
        "checks": checks,
        "passed": passed,
        "total": total,
        "score": score,
        "result": "PASS" if score == 1.0 else "FAIL"
    }
def evaluate_numerical(test, answer):
    try:
        expected = float(test["expected_answer"])
        actual = float(answer.strip())
    except (ValueError, AttributeError):
        return {
            "passed": 0,
            "total": 1,
            "score": 0.0,
            "result": "FAIL"
        }

    tolerance = 1e-6
    passed = abs(actual - expected) <= tolerance

    return {
        "passed": 1 if passed else 0,
        "total": 1,
        "score": 1.0 if passed else 0.0,
        "result": "PASS" if passed else "FAIL"
    }
from code_executor import execute_code

def evaluate_code_execution(test, answer):

    execution = execute_code(answer)

    if not execution["success"]:
        return {
            "passed": 0,
            "total": 1,
            "score": 0.0,
            "result": "FAIL",
            "error": execution["error"]
        }

    namespace = execution["namespace"]

    config = test.get("evaluation_config", {})

    function_name = config.get("function_name")
    test_cases = config.get("test_cases", [])

    if not function_name:
        return {
            "passed": 0,
            "total": 1,
            "score": 0.0,
            "result": "FAIL",
            "error": "No function name specified."
        }

    if function_name not in namespace:
        return {
            "passed": 0,
            "total": 1,
            "score": 0.0,
            "result": "FAIL",
            "error": f"Function '{function_name}' was not found."
        }

    function = namespace[function_name]

    passed = 0

    for test_case in test_cases:

        inputs = test_case["input"]
        expected = test_case["expected"]

        try:

            if test_case.get("multiple_args", False):
                actual = function(*inputs)
            else:
                actual = function(inputs)

            if actual == expected:
                passed += 1

        except Exception:
            pass

    total = len(test_cases)

    score = passed / total if total > 0 else 0

    return {
        "passed": passed,
        "total": total,
        "score": score,
        "result": "PASS" if score == 1.0 else "FAIL"
    }