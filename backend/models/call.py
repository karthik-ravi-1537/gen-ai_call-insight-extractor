# models/call.py

import uuid
from datetime import datetime

from models.base import Base, AuditMixin
from models.enums import CallStatus
from sqlalchemy import Column, Text, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Call(Base, AuditMixin):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_summary = Column(Text, nullable=True)
    processed_summary = Column(Text, nullable=True)
    call_status = Column(Enum(CallStatus), default=CallStatus.UPLOADED, nullable=False)
    call_llm_retry_count = Column(Integer, default=0)
    call_llm_summary_updated_at = Column(DateTime, default=datetime.utcnow)

    transcripts = relationship("Transcript", back_populates="call")
