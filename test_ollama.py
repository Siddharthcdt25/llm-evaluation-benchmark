import os
import subprocess

OLLAMA = os.path.join(
    os.environ["LOCALAPPDATA"],
    "Programs",
    "Ollama",
    "ollama.exe"
)

result = subprocess.run(
    [
        OLLAMA,
        "run",
        "llama3.2:3b",
        "What is the capital of France?"
    ],
    capture_output=True,
    text=True
)

print("MODEL RESPONSE:")
print(result.stdout)

if result.stderr:
    print("\nERROR:")
    print(result.stderr)