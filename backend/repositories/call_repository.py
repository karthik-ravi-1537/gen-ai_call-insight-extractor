# repositories/call_repository.py

from uuid import UUID

from models.entities.call import Call
from sqlalchemy.orm import Session


def save(db: Session, call: Call):
    """Save an existing object to the database."""
    db.add(call)
    db.commit()
    db.refresh(call)


def create(db: Session) -> Call:
    call = Call()
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def get_by_id(db: Session, call_id: UUID) -> Call:
    return db.query(Call).filter(Call.id == call_id).first()
