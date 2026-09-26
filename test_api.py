from model_client import ask_model

question = "Explain artificial intelligence in one sentence."

answer = ask_model(question)

print("\nModel response:")
print("-" * 50)
print(answer)
print("-" * 50)