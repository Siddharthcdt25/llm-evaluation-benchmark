import json


def ask_mock_model(question, expected_answer):

    if isinstance(expected_answer, str):
        answer = expected_answer
    else:
        answer = json.dumps(expected_answer)

    return {
        "success": True,
        "answer": answer,
        "error": None
    }