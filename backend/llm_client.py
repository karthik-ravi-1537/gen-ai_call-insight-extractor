# llm_client.py

import json
from datetime import date

from openai import OpenAI

from config import loaded_config

config = loaded_config


# --- LLM Client Class ---
class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.LLM_API_KEY)

    def process_transcript(self, transcript_text: str) -> dict:
        prompt = (
            "Extract the following information from the transcript:\n"
            "  - payment_status (prepaid, collected, or committed)\n"
            "  - payment_amount (numeric value only, without currency symbols)\n"
            "  - payment_date (in YYYY-MM-DD format)\n"
            "  - payment_method\n"
            "  - summary_text: a brief summary of the conversation.\n\n"
            "Transcript:\n"
            f"{transcript_text}\n\n"
            "Return the result in JSON format."
        )
        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a conversation insights extractor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150,
            )
            llm_response = response.choices[0].message.content.strip()
            data = json.loads(llm_response)

            # Convert payment_amount to float if it contains currency symbols
            if "payment_amount" in data and data["payment_amount"]:
                # Handle if it's already a number
                if isinstance(data["payment_amount"], (int, float)):
                    data["payment_amount"] = float(data["payment_amount"])
                else:
                    # Remove currency symbols, commas and whitespace
                    amount_str = str(data["payment_amount"]).replace('$', '').replace('€', '') \
                        .replace('£', '').replace(',', '') \
                        .replace(' ', '')
                    try:
                        data["payment_amount"] = float(amount_str)
                    except ValueError:
                        # Fallback if conversion fails
                        data["payment_amount"] = 0.0

            return data
        except Exception as e:
            print("OpenAI processing error:", e)
            return {
                "payment_status": "committed",
                "payment_amount": 100.00,
                "payment_date": date.today().isoformat(),
                "payment_method": "Credit Card",
                "summary_text": "Fallback summary: Payment committed as per transcript."
            }

    def process_call_summary(self, raw_summary: str) -> str:
        prompt = (
            "Based on the following raw transcript summaries, generate a concise, refined call summary:\n"
            f"{raw_summary}\n\n"
            "Return only the summary text."
        )
        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a call summary generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150,
            )
            processed_summary = response.choices[0].message.content.strip()
            return processed_summary
        except Exception as e:
            print("OpenAI call summary processing error:", e)
            return "Fallback processed summary: " + raw_summary


# --- LLM Initialization Function ---
def init_llm():
    """
    Initializes the LLM client based on the configuration.
    Returns an object with two methods:
      - process_transcript(transcript_text: str) -> dict
      - process_call_summary(raw_summary: str) -> str
    """
    if config.LLM == "openai":
        return OpenAIClient()
    else:
        raise Exception("Unsupported LLM provider: " + config.LLM)


# Create a singleton client instance
_client = init_llm()


# Module-level functions that delegate to the client instance
def process_transcript(transcript_text: str) -> dict:
    return _client.process_transcript(transcript_text)


def process_call_summary(raw_summary: str) -> str:
    return _client.process_call_summary(raw_summary)
