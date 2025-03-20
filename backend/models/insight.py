# models/insight.py

import uuid
from datetime import datetime

from models.base import Base, AuditMixin
from models.enums import PaymentStatus, PaymentCurrency
from sqlalchemy import Column, Text, DateTime, Numeric, Date, Boolean, Integer, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Insight(Base, AuditMixin):
    __tablename__ = "insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"), nullable=False, unique=True)

    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_amount = Column(Numeric(10, 2), nullable=True, default=0.0)
    payment_currency = Column(Enum(PaymentCurrency), nullable=False, default=PaymentCurrency.USD)
    payment_date = Column(Date, nullable=True)
    payment_method = Column(String, nullable=True)

    summary_text = Column(Text, nullable=True)  # LLM-generated summary
    llm_summary_updated_at = Column(DateTime, default=datetime.utcnow)

    user_modified_summary = Column(Text, nullable=True)
    user_summary_updated_at = Column(DateTime, nullable=True)

    llm_redo_required = Column(Boolean, default=False)
    llm_retry_count = Column(Integer, default=0)  # Maximum allowed: 5 retries

    transcript = relationship("Transcript", back_populates="insight")
