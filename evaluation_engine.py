import json

from evaluator import (
    evaluate_reasoning_006,
    evaluate_numerical,
    evaluate_code_execution
)


def evaluate_test(test, answer):
    evaluation_type = test["evaluation_type"]

    if evaluation_type == "rule_based":
        return evaluate_rule_based(test, answer)

    elif evaluation_type == "exact_match":
        return evaluate_exact_match(test, answer)

    elif evaluation_type == "numerical":
        return evaluate_numerical(test, answer)

    elif evaluation_type == "code_execution":
       return evaluate_code_execution(test, answer)

    elif evaluation_type == "schema_validation":
        return evaluate_schema_validation(test, answer)


    else:
        return {
            "result": "NOT_IMPLEMENTED",
            "score": None,
            "message": f"Evaluation type '{evaluation_type}' is not implemented yet."
        }

def evaluate_rule_based(test, answer):
    test_id = test["id"]

    if test_id == "REASONING_006":
        return evaluate_reasoning_006(answer)

    if test_id == "INSTRUCTION_003":
        words = answer.strip().split()

        passed = len(words) == 5

        return {
            "passed": 1 if passed else 0,
            "total": 1,
            "score": 1.0 if passed else 0.0,
            "result": "PASS" if passed else "FAIL"
        }

    if test_id == "INSTRUCTION_004":
        lines = answer.strip().splitlines()

        passed = (
            len(lines) == 2
            and all(line.startswith("-") for line in lines)
        )

        return {
            "passed": 1 if passed else 0,
            "total": 1,
            "score": 1.0 if passed else 0.0,
            "result": "PASS" if passed else "FAIL"
        }

    if test_id == "INSTRUCTION_009":
        text = answer.strip()

        passed = (
            len(text.splitlines()) == 1
            and "artificial intelligence" in text.lower()
            and "machine learning" in text.lower()
            and "neural network" in text.lower()
            and ":" not in text
        )

        return {
            "passed": 1 if passed else 0,
            "total": 1,
            "score": 1.0 if passed else 0.0,
            "result": "PASS" if passed else "FAIL"
        }

    return {
        "result": "NOT_IMPLEMENTED",
        "score": None,
        "message": f"No rule-based evaluator exists for '{test_id}'."
    }


def evaluate_exact_match(test, answer):
    expected_answer = test["expected_answer"]

    answer_normalized = answer.strip().lower()
    expected_normalized = str(expected_answer).strip().lower()

    passed = answer_normalized == expected_normalized

    return {
        "passed": 1 if passed else 0,
        "total": 1,
        "score": 1.0 if passed else 0.0,
        "result": "PASS" if passed else "FAIL"
    }
def evaluate_schema_validation(test, answer):
    try:
        data = json.loads(answer)
    except json.JSONDecodeError:
        return {
            "passed": 0,
            "total": 1,
            "score": 0.0,
            "result": "FAIL"
        }

    config = test.get("evaluation_config", {})

    required_keys = set(config.get("required_keys", []))
    allowed_keys = set(config.get("allowed_keys", []))

    actual_keys = set(data.keys())

    correct_keys = (
        actual_keys == required_keys
        and actual_keys.issubset(allowed_keys)
    )

    if correct_keys:
        return {
            "passed": 1,
            "total": 1,
            "score": 1.0,
            "result": "PASS"
        }

    return {
        "passed": 0,
        "total": 1,
        "score": 0.0,
        "result": "FAIL"
    }
