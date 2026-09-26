from ollama_model_client import ask_ollama


response = ask_ollama(
    "What is the capital of France?"
)

print("Success:", response["success"])
print("Answer:", response["answer"])
print("Error:", response["error"])