from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class VerificationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    REJECTED = "REJECTED"

class WorkRecord(Base):
    __tablename__ = "work_records"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    worker_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # Dapat ditautkan setelah klaim aman[cite: 6]
    title = Column(String, nullable=False)
    tasks = Column(Text, nullable=False)
    skills = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.DRAFT)
    verified_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    business = relationship("Business")

class WorkRecordClaim(Base):
    __tablename__ = "work_record_claims"

    id = Column(Integer, primary_key=True, index=True)
    work_record_id = Column(Integer, ForeignKey("work_records.id", ondelete="CASCADE"), nullable=False)
    worker_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="PENDING") # PENDING, APPROVED, REJECTED
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)