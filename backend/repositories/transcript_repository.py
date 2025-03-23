# repositories/transcript_repository.py

from datetime import datetime, timezone
from uuid import UUID

from models.entities.transcript import Transcript
from sqlalchemy.orm import Session


def save(db: Session, transcript: Transcript):
    """Save an existing object to the database."""
    db.add(transcript)
    db.commit()
    db.refresh(transcript)


def create(db: Session, call_id: UUID, file_name: str, transcript_text: str, file_content: str) -> Transcript:
    transcript = Transcript(
        call_id=call_id,
        file_name=file_name,
        transcript_text=transcript_text,
        file_content=file_content,
        created_at=datetime.now(timezone.utc),
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def get_by_call_id(db: Session, call_id: UUID) -> Transcript:
    return db.query(Transcript).filter(Transcript.call_id == call_id).all()
