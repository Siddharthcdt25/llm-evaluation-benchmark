import os
import subprocess


OLLAMA = os.path.join(
    os.environ["LOCALAPPDATA"],
    "Programs",
    "Ollama",
    "ollama.exe"
)

MODEL = "llama3.2:3b"


def ask_ollama(question):

    try:

        result = subprocess.run(
    [
        OLLAMA,
        "run",
        MODEL,
        question
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=120
)

        if result.returncode != 0:
            return {
                "success": False,
                "answer": None,
                "error": result.stderr.strip()
            }

        return {
            "success": True,
            "answer": result.stdout.strip(),
            "error": None
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "answer": None,
            "error": "Ollama request timed out."
        }

    except Exception as e:

        return {
            "success": False,
            "answer": None,
            "error": str(e)
        }