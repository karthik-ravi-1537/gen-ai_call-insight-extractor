# llm_client.py

import json

from config import loaded_config
from openai import OpenAI

config = loaded_config


# --- LLM Client Class ---
class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.LLM_API_KEY)

    def process_call_summary(self, raw_summary: str) -> str:
        system_prompt = (
            "You are an expert call summarization assistant specializing in customer service interactions. "
            "Your task is to create clear, accurate, and concise summaries that capture key information "
            "including: main topics discussed, customer concerns, agent responses, and any resolutions or "
            "action items. Maintain factual accuracy and professional tone."
        )

        # Check if we have multiple summaries
        if " ||| " in raw_summary:
            # Split and format the summaries
            individual_summaries = raw_summary.split(" ||| ")
            formatted_summaries = "\n\n".join([f"Transcript {i + 1}:\n{summary}"
                                               for i, summary in enumerate(individual_summaries)])

            user_prompt = (
                "You have multiple transcript summaries from the same call that need to be combined into "
                "a single coherent summary. Here are the individual summaries:\n\n"
                f"{formatted_summaries}\n\n"
                "Create a unified, comprehensive summary that:\n"
                "1. Consolidates all key information from each transcript\n"
                "2. Eliminates redundancies\n"
                "3. Presents details in a logical flow\n"
                "4. Maintains a professional tone\n\n"
                "Provide only the final summary without any explanations or meta-commentary."
            )
        else:
            # Single summary case - use existing logic
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
            ai_summary = response.choices[0].message.content.strip()
            return ai_summary
        except Exception as e:
            print("OpenAI processing error in process_call_summary():", e)
            # For multiple summaries, provide a basic concatenation as fallback
            if " ||| " in raw_summary:
                summaries = raw_summary.split(" ||| ")
                return "Multiple transcript summary (error processing): " + " ".join(
                    [f"[Transcript {i + 1}] {s[:100]}..." for i, s in enumerate(summaries)]
                )
            return "Fallback AI summary: " + raw_summary

    def process_transcript_text(self, transcript_text: str) -> dict:
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
            "  - ai_summary: A concise summary of the key points in the conversation\n\n"
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
            print("OpenAI processing error in process_transcript():", e)
            return {
                "payment_status": "Pending",
                "payment_amount": None,
                "payment_currency": None,
                "payment_date": None,
                "payment_method": None,
                "comments": None,
                "summary_text": f"Error processing transcript: {str(e)}. This is a fallback response and requires manual review."
            }

    def generate_refined_summary(self, base_summary: str, user_summary: str) -> str:
        """
        Generate a refined summary by combining the base summary with user feedback.

        Args:
            base_summary (str): The existing summary (either LLM-generated or previously refined)
            user_summary (str): The user's modified summary

        Returns:
            str: The refined summary incorporating user feedback
        """
        try:
            prompt = f"""
                    You are tasked with creating an improved summary of a call transcript.
            
                    Here is the original AI-generated summary:
                    ---
                    {base_summary}
                    ---
            
                    Here is the human expert's version of the summary:
                    ---
                    {user_summary}
                    ---
            
                    Please create a refined summary that:
                    1. Preserves the important details highlighted by the human expert
                    2. Maintains good structure and readability from the AI summary
                    3. Incorporates any factual corrections from the human version
                    4. Is written in a professional, clear tone suitable for business context
            
                    Produce a single cohesive summary paragraph.
                    """

            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that refines summaries based on expert feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=1024
            )

            refined_summary = response.choices[0].message.content.strip()
            return refined_summary

        except Exception as e:
            print(f"OpenAI processing error in generate_refined_summary(): {str(e)}")
            return "Fallback refined summary: " + base_summary


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
def process_call_summary(raw_summary: str) -> str:
    return _client.process_call_summary(raw_summary)


def process_transcript_text(transcript_text: str) -> dict:
    return _client.process_transcript_text(transcript_text)


def generate_refined_summary(base_summary: str, user_summary: str) -> str:
    return _client.generate_refined_summary(base_summary, user_summary)
