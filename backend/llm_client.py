# llm_client.py

import json

from openai import OpenAI

from config import loaded_config

config = loaded_config


# --- LLM Client Class ---
class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.LLM_API_KEY)

    def process_transcript(self, transcript_text: str) -> dict:
        system_prompt = (
            "You are an expert conversation analyzer specializing in financial call transcripts. "
            "Extract payment details with precision from customer service interactions. Focus on "
            "identifying payment status, amounts, dates, and methods while maintaining factual accuracy. "
            "Ignore irrelevant conversation elements and provide output strictly in the requested JSON format."
        )

        user_prompt = (
            "Extract the following information from the transcript:\n"
            "  - payment_status: Must be one of [Prepaid, Collected, Committed, Pending]\n"
            "  - payment_amount: Numeric value only, without currency symbols\n"
            "  - payment_currency: Currency code [USD, INR, EUR, GBP, JPY, AUD, Other]\n"
            "  - payment_date: In YYYY-MM-DD format\n"
            "  - payment_method: One of [Credit Card, Debit Card, ACH, Check, Cash, Wire Transfer, Other]\n"
            "    If 'Other', format as 'Other - [specific method]'\n"
            "  - summary_text: A concise summary of the key points in the conversation\n\n"
            "Transcript:\n"
            f"{transcript_text}\n\n"
            "Return the result in valid JSON format."
        )

        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=1024
            )
            llm_response = response.choices[0].message.content.strip()
            data = json.loads(llm_response)

            # Standardize the payment_status to lowercase
            if "payment_status" in data:
                data["payment_status"] = data["payment_status"].lower()

            # Convert payment_amount to float if it contains currency symbols
            if "payment_amount" in data and data["payment_amount"] is not None:
                # Handle if it's already a number
                if isinstance(data["payment_amount"], (int, float)):
                    data["payment_amount"] = float(data["payment_amount"])
                else:
                    # Remove currency symbols, commas and whitespace
                    amount_str = str(data["payment_amount"])
                    # Replace common currency symbols and formatting characters
                    replacements = ['$', '₹', '€', '£', '¥', ',', ' ']
                    for char in replacements:
                        amount_str = amount_str.replace(char, '')

                    try:
                        data["payment_amount"] = float(amount_str)
                    except ValueError:
                        # Fallback if conversion fails
                        print(f"Could not convert payment amount: '{data['payment_amount']}'")
                        data["payment_amount"] = None

            # Standardize the currency code to uppercase
            if "payment_currency" in data and data["payment_currency"]:
                data["payment_currency"] = data["payment_currency"].upper()

            return data
        except Exception as e:
            print("OpenAI processing error:", e)
            return {
                "payment_status": "Pending",
                "payment_amount": None,
                "payment_currency": None,
                "payment_date": None,
                "payment_method": None,
                "comments": None,
                "summary_text": f"Error processing transcript: {str(e)}. This is a fallback response and requires manual review."
            }

    def process_call_summary(self, raw_summary: str) -> str:
        system_prompt = (
            "You are an expert call summarization assistant specializing in customer service interactions. "
            "Your task is to create clear, accurate, and concise summaries that capture key information "
            "including: main topics discussed, customer concerns, agent responses, and any resolutions or "
            "action items. Maintain factual accuracy and professional tone."
        )

        user_prompt = (
            "Analyze the following call transcript summary and create a refined, professional summary:\n\n"
            f"{raw_summary}\n\n"
            "Focus on extracting key information like:\n"
            "- Main reason for the call\n"
            "- Important customer details or concerns\n"
            "- Resolutions or agreements reached\n"
            "- Any follow-up actions\n\n"
            "Provide only the final summary without any explanations or meta-commentary."
        )

        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1024,
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
