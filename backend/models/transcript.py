# models/transcript.py

import uuid
from datetime import datetime, timezone

from models.base import Base, AuditMixin
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Transcript(Base, AuditMixin):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    file_name = Column(String, nullable=False)
    transcript_text = Column(Text, nullable=False)
    file_content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)

    call = relationship("Call", back_populates="transcripts")
    insight = relationship("Insight", uselist=False, back_populates="transcript")
