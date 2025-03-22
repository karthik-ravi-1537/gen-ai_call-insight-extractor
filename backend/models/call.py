# models/call.py

import uuid

from models.base import Base, AuditMixin
from models.enums import CallStatus
from sqlalchemy import Column, Text, DateTime, Integer, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Call(Base, AuditMixin):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_status = Column(Enum(CallStatus), default=CallStatus.UPLOADED, nullable=False)

    raw_summary = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_summary_updated_at = Column(DateTime, nullable=True)

    llm_refinement_required = Column(Boolean, default=False)
    llm_refinement_count = Column(Integer, default=0)

    transcripts = relationship("Transcript", back_populates="call")
