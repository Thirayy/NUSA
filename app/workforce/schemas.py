from pydantic import BaseModel
from typing import Optional, List
from app.workforce.models import JobStatus, ApplicationStatus

class WorkerProfileCreate(BaseModel):
    display_name: str
    summary: Optional[str] = None
    location: str
    availability: Optional[str] = None

class WorkerProfileResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    summary: Optional[str]
    location: str
    availability: Optional[str]

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    description: str
    location: str
    employment_type: str
    requirements: str

class JobResponse(BaseModel):
    id: int
    business_id: int
    title: str
    description: str
    location: str
    employment_type: str
    requirements: str
    status: JobStatus

    class Config:
        from_attributes = True

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    worker_user_id: int
    status: ApplicationStatus

    class Config:
        from_attributes = True