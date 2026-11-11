
from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import json

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found.")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


def explain_results(user_question: str, query_results):
    """
    Convert actual MySQL query results into
    a clear natural-language explanation.
    """

    prompt = f"""
You are an expert hotel booking data analyst.

USER QUESTION:
{user_question}

ACTUAL MYSQL QUERY RESULTS:
{json.dumps(query_results, default=str)}

INSTRUCTIONS:
1. Answer the user's question directly.
2. Use only the supplied database results.
3. Do not invent or assume any statistics.
4. Format large numbers with commas.
5. Explain important findings in simple language.
6. If results are empty, clearly state that no matching
   records were found.
7. Do not claim correlation or causation without evidence.
8. Keep the response concise and professional.

Provide the final answer in natural language.
"""

    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt
    )

    answer = (response.output_text or "").strip()

    if not answer:
        raise ValueError("Gemini returned an empty explanation.")

    return answer
