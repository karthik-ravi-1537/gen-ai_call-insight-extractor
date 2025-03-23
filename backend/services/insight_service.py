# services/insight_service.py

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from clients import llm_client
from constants.constants import MAX_LLM_RETRY_COUNT
from models.entities.insight import Insight
from repositories import insight_repository
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def create_insight(
        db: Session,
        transcript_id: UUID,
        payment_status,
        payment_amount,
        payment_currency,
        payment_date,
        payment_method,
        ai_summary,
        ai_summary_updated_at,
        comments,
        summary_history
) -> Insight:
    """
    Create a new insight based on transcript processing results.
    """
    insight = insight_repository.create(
        db=db,
        transcript_id=transcript_id,
        payment_status=payment_status,
        payment_amount=payment_amount,
        payment_currency=payment_currency,
        payment_date=payment_date,
        payment_method=payment_method,
        ai_summary=ai_summary,
        ai_summary_updated_at=ai_summary_updated_at,
        comments=comments,
        summary_history=summary_history,
    )

    return insight


def get_insight(db: Session, insight_id: UUID) -> Insight:
    """
    Get an insight by its ID.
    """
    return insight_repository.get_by_id(db, insight_id)


def save_insight(db: Session, insight: Insight) -> Insight:
    """
    Save an existing insight object to the database.
    """
    insight = insight_repository.save(db, insight)
    return insight


def get_insight_by_transcript_id(db: Session, transcript_id: UUID) -> Insight:
    """
    Get an insight by its transcript ID.
    """
    return insight_repository.get_by_transcript_id(db, transcript_id)


def update_user_summary(db: Session, insight_id: str, user_summary: str) -> Insight:
    """
    Update the user-modified summary for a transcript insight.
    This sets a flag indicating that an LLM redo might be required.
    """
    insight = get_insight(db, UUID(insight_id))

    if not insight:
        raise Exception("Insight not found")

    insight.user_summary = user_summary
    insight.user_summary_updated_at = datetime.now(timezone.utc)
    insight.llm_refinement_required = True

    save_insight(db, insight)
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
