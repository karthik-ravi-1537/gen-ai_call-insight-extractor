# services/transcript_service.py
import asyncio
import logging
from datetime import datetime, timezone, date
from uuid import UUID

import llm_client
from constants.constants import MAX_LLM_RETRY_COUNT
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
    llm_data = await asyncio.to_thread(llm_client.process_transcript, transcript.transcript_text)

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
    """
    Update the user-modified summary for a transcript insight.
    This sets a flag indicating that an LLM redo might be required.
    """
    insight = insight_service.get_insight(db, UUID(insight_id))

    if not insight:
        raise Exception("Insight not found")

    insight.user_summary = user_summary
    insight.user_summary_updated_at = datetime.now(timezone.utc)
    insight.llm_refinement_required = True

    insight_service.save_insight(db, insight)
    return insight


async def generate_refined_summary(db: Session, insight_id: str) -> Insight:
    """
    Generate a refined summary combining user's summary with either
    existing refined summary or original LLM summary.
    """
    try:
        insight = db.query(Insight).filter(Insight.id == UUID(insight_id)).first()

        if not insight:
            logger.error(f"Insight with ID {insight_id} not found")
            raise Exception("Insight not found!")

        if not insight.user_summary:
            logger.warning(f"No user-modified summary found for insight {insight_id}")
            return insight

        if insight.llm_refinement_count >= MAX_LLM_RETRY_COUNT:
            logger.warning(f"Maximum LLM retry count reached for insight {insight_id}")
            insight.llm_refinement_required = False
            db.commit()
            return insight

        base_summary = insight.refined_summary if insight.refined_summary else insight.ai_summary

        refined_summary = await asyncio.to_thread(
            llm_client.generate_refined_summary,
            base_summary=base_summary,
            user_summary=insight.user_summary
        )

        current_time = datetime.now(timezone.utc)

        history_entry = {
            "timestamp": current_time.isoformat(),
            "ai_summary": insight.ai_summary,
            "user_summary": insight.user_summary,
            "refined_summary": insight.refined_summary
        }

        current_history = insight.summary_history.copy() if insight.summary_history else []
        current_history.append(history_entry)
        insight.summary_history = current_history

        insight.refined_summary = refined_summary
        insight.refined_summary_updated_at = current_time
        insight.llm_refinement_required = False
        insight.llm_refinement_count += 1

        db.commit()
        return insight

    except Exception as e:
        logger.error(f"Failed to generate refined summary: {str(e)}")
        raise Exception(f"Failed to generate refined summary: {str(e)}")
