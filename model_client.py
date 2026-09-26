import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv("GEMINI_MODEL")


def ask_model(question, max_retries=3):

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=question
            )

            return {
                "success": True,
                "answer": response.text,
                "error": None
            }

        except errors.ServerError as e:

            if attempt == max_retries - 1:

                return {
                    "success": False,
                    "answer": None,
                    "error": str(e)
                }

            wait_time = 2 ** attempt

            print(
                f"API temporarily unavailable. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

        except Exception as e:

            return {
                "success": False,
                "answer": None,
                "error": str(e)
            }