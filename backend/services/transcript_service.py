# services/transcript_service.py
import asyncio
import logging
from datetime import datetime, timezone, date
from uuid import UUID

from clients import llm_client
from fastapi import UploadFile, HTTPException
from models.entities.insight import Insight
from models.entities.transcript import Transcript
from models.enums import PaymentStatus, PaymentCurrency, PaymentMethod
from repositories import transcript_repository
from services import insight_service
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


async def create_transcript(
        db: Session,
        call_id: UUID,
        file: UploadFile
) -> Transcript:
    """
    Create a new transcript entry in the database and return it.
    """
    try:
        content = await file.read()
        transcript_text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file {file.filename}") from e

    transcript = transcript_repository.create(
        db=db,
        call_id=call_id,
        file_name=file.filename,
        transcript_text=transcript_text,
        file_content=content.decode("utf-8")
    )

    return transcript


def get_transcripts_by_call_id(
        db: Session,
        call_id: UUID
) -> list[Transcript]:
    """
    Retrieve all transcripts for a given call ID.
    """
    transcripts = transcript_repository.get_by_call_id(db, call_id)
    if not transcripts:
        return []
    return transcripts


async def process_transcript(db: Session, transcript: Transcript):
    """
    Process a transcript using the LLM client and return the generated insight.
    """
    llm_data = await asyncio.to_thread(llm_client.process_transcript_text, transcript.transcript_text)

    payment_date = None
    if llm_data.get("payment_date"):
        try:
            payment_date = date.fromisoformat(llm_data.get("payment_date"))
        except ValueError:
            payment_date = None

    comments = llm_data.get("comments")

    if llm_data.get("payment_method") and "Other - " in llm_data.get("payment_method"):
        llm_data["payment_method"] = "Other"
        comments = f"{comments}\nSpecific Payment Method: {llm_data.get('payment_method').split('Other - ')[1]}" \
            if comments \
            else f"Specific Payment Method: {llm_data.get('payment_method').split('Other - ')[1]}"

    if llm_data.get("payment_currency") and "Other - " in llm_data.get("payment_currency"):
        llm_data["payment_currency"] = "Other"
        comments = f"{comments}\nSpecific Payment Currency: {llm_data.get('payment_currency').split('Other - ')[1]}" \
            if comments \
            else f"Specific Payment Currency: {llm_data.get('payment_currency').split('Other - ')[1]}"

    payment_status = PaymentStatus.from_string(llm_data.get("payment_status", "").capitalize())
    payment_currency = PaymentCurrency.from_string(llm_data.get("payment_currency", ""))
    payment_method = PaymentMethod.from_string(llm_data.get("payment_method", ""))

    current_time = datetime.now(timezone.utc)
    ai_summary = llm_data.get("ai_summary", "")

    history_entry = {
        "timestamp": current_time.isoformat(),
        "ai_summary": ai_summary,
        "user_summary": "",
        "refined_summary": "",
    }

    summary_history = [history_entry]

    insight = insight_service.create_insight(
        db,
        transcript.id,
        payment_status,
        llm_data.get("payment_amount"),
        payment_currency,
        payment_date,
        payment_method,
        ai_summary,
        current_time,
        comments,
        summary_history
    )

    transcript.processed_at = current_time
    db.commit()
    return insight


def update_user_summary(db: Session, insight_id: str, user_summary: str) -> Insight:
    return insight_service.update_user_summary(db, insight_id, user_summary)


async def generate_refined_summary(db: Session, insight_id: str) -> Insight:
    return await insight_service.generate_refined_summary(db, insight_id)
