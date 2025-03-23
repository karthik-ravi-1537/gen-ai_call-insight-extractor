# models/entities/insight.py

import uuid

from models.entities.base import Base, AuditMixin
from models.enums import PaymentStatus, PaymentCurrency, PaymentMethod
from sqlalchemy import Column, Text, DateTime, Numeric, Date, Boolean, Integer, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Insight(Base, AuditMixin):
    __tablename__ = "insight"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcript.id"), nullable=False, unique=True)

    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_amount = Column(Numeric(10, 2), nullable=True, default=0.0)
    payment_currency = Column(Enum(PaymentCurrency), nullable=False, default=PaymentCurrency.USD)
    payment_date = Column(Date, nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    comments = Column(Text, nullable=True)

    ai_summary = Column(Text, nullable=True)
    ai_summary_updated_at = Column(DateTime, nullable=True)

    user_summary = Column(Text, nullable=True)
    user_summary_updated_at = Column(DateTime, nullable=True)

    refined_summary = Column(Text, nullable=True)
    refined_summary_updated_at = Column(DateTime, nullable=True)

    summary_history = Column(JSON, nullable=True)

    llm_refinement_required = Column(Boolean, default=False)
    llm_refinement_count = Column(Integer, default=0)

    transcript = relationship("Transcript", back_populates="insight")
