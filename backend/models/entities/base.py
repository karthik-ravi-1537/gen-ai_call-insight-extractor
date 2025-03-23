# models/entities/base.py

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuditMixin:
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    updated_by = Column(Integer, default=1)
    record_status = Column(String, default="Active")
