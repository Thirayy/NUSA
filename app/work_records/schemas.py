from pydantic import BaseModel
from typing import Optional
from app.work_records.models import VerificationStatus

class WorkRecordCreate(BaseModel):
    title: str
    tasks: str
    skills: str
    start_date: str
    end_date: Optional[str] = None
    worker_user_id: Optional[int] = None

class WorkRecordResponse(BaseModel):
    id: int
    business_id: int
    title: str
    tasks: str
    skills: str
    start_date: str
    end_date: Optional[str]
    verification_status: VerificationStatus

    class Config:
        from_attributes = True

class CorrectionRequestCreate(BaseModel):
    note: str