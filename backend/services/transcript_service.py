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

        # Check if maximum retry limit reached
        if insight.llm_refinement_count >= 5:
            raise Exception("Maximum LLM retry count reached!")

        # Determine base summary for refinement
        base_summary = insight.refined_summary if insight.refined_summary else insight.ai_summary

        # Generate new refined summary
        refined_summary = await asyncio.to_thread(
            llm_client.generate_refined_summary,
            base_summary=base_summary,
            user_summary=insight.user_summary
        )

        # Only proceed with database updates after successful LLM call
        current_time = datetime.now(timezone.utc)

        # Prepare history entry
        history_entry = {
            "timestamp": current_time.isoformat(),
            "llm_summary": insight.ai_summary,
            "user_summary": insight.user_summary,
            "refined_summary": insight.refined_summary
        }

        # Initialize summary_history if needed
        if not insight.summary_history:
            insight.summary_history = []

        # Add current entry to history without explicit limitation
        insight.summary_history.append(history_entry)

        # Update insight with new data
        insight.refined_summary = refined_summary
        insight.refined_at = current_time
        insight.llm_refinement_required = False
        insight.llm_refinement_count += 1

        # Commit all changes at once
        db.commit()
        return insight

    except Exception as e:
        logger.error(f"Failed to generate refined summary: {str(e)}")
        raise Exception(f"Failed to generate refined summary: {str(e)}")
