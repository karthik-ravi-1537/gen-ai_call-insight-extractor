# services/transcript_service.py
import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

import llm_client
from models.insight import Insight
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def update_user_summary(db: Session, insight_id: str, user_summary: str) -> Insight:
    """
    Update the user-modified summary for a transcript insight.
    This sets a flag indicating that an LLM redo might be required.
    """
    insight = db.query(Insight).filter(Insight.id == UUID(insight_id)).first()

    if not insight:
        raise Exception("Insight not found")

    insight.user_summary = user_summary
    insight.user_summary_updated_at = datetime.now(timezone.utc)
    insight.llm_refinement_required = True

    db.commit()
    return insight


async def generate_refined_summary(db: Session, insight_id: str) -> Insight:
    """
    Generate a refined summary combining user's summary with either
    existing refined summary or original LLM summary.
    """
    try:
        insight = db.query(Insight).filter(Insight.id == UUID(insight_id)).first()

        if not insight:
            raise Exception("Insight not found!")

        if not insight.user_summary:
            raise Exception("No user-modified summary found!")

        if insight.llm_refinement_count >= 5:
            raise Exception("Maximum LLM retry count reached!")

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
