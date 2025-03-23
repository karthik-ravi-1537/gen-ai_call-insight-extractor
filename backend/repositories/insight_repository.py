# repositories/insight_repository.py

from uuid import UUID

from models.entities.insight import Insight
from sqlalchemy.orm import Session


def save(db: Session, insight: Insight):
    """Save an existing object to the database."""
    db.add(insight)
    db.commit()
    db.refresh(insight)


def create(
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
    Create a new insight entry in the database and return it.
    """
    insight = Insight(
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
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def get_by_id(db: Session, insight_id: UUID) -> Insight:
    """
    Retrieve an insight by its ID.
    """
    return db.query(Insight).filter(Insight.id == insight_id).first()


def get_by_transcript_id(db: Session, transcript_id: UUID) -> Insight:
    """
    Retrieve an insight by its transcript ID.
    """
    return db.query(Insight).filter(Insight.transcript_id == transcript_id).first()
