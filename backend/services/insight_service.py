# services/insight_service.py

import logging
from uuid import UUID

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
