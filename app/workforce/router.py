from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import hash_token
from app.auth.models import User, Session as UserSession, UserRole
from app.businesses.models import Business
from app.workforce.models import (
    WorkerProfile, Job, Application, JobStatus, 
    ApplicationStatus, WorkerSkill, Skill, Employee, EmployeeStatus, WorkRecord, VerificationStatus
)
from app.workforce.schemas import (
    WorkerProfileCreate, WorkerProfileResponse,
    JobCreate, JobResponse, ApplicationResponse
)

router = APIRouter(prefix="/api/v1", tags=["Workforce & Jobs"])

def get_current_user_from_cookie(nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)) -> User:
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan.")
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    if not session_record:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Pengguna tidak ditemukan.")
    return user

# --- Profil Pekerja ---
@router.post("/worker/profile", response_model=WorkerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_worker_profile(payload: WorkerProfileCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    if user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Hanya role WORKER yang dapat membuat profil pekerja.")
    
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user.id).first()
    if profile:
        profile.display_name = payload.display_name
        profile.summary = payload.summary
        profile.location = payload.location
        profile.availability = payload.availability
    else:
        profile = WorkerProfile(
            user_id=user.id,
            display_name=payload.display_name,
            summary=payload.summary,
            location=payload.location,
            availability=payload.availability
        )
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/worker/profile/me", response_model=WorkerProfileResponse)
def get_my_worker_profile(nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil pekerja belum dibuat.")
    return profile

# --- Lowongan Kerja (Jobs) oleh Employer Owner ---
@router.post("/businesses/{business_id}/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(business_id: int, payload: JobCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    business = db.query(Business).filter(Business.id == business_id).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Bisnis tidak ditemukan.")

    if business.owner_user_id != user.id or user.role != UserRole.EMPLOYER_OWNER:
        raise HTTPException(status_code=403, detail="Hanya Pemilik Usaha (Owner) yang berhak mempublikasikan lowongan kerja.")

    job = Job(
        business_id=business.id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        employment_type=payload.employment_type,
        requirements=payload.requirements,
        status=JobStatus.OPEN
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/jobs", response_model=List[JobResponse])
def list_open_jobs(db: DBSession = Depends(get_db)):
    return db.query(Job).filter(Job.status == JobStatus.OPEN).all()

# --- Lamaran Pekerjaan (Applications) oleh Worker ---
@router.post("/jobs/{job_id}/applications", status_code=status.HTTP_201_CREATED, response_model=ApplicationResponse)
def apply_to_job(job_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    if user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Hanya pekerja yang dapat melamar lowongan.")
    
    job = db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.OPEN).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan atau sudah ditutup.")

    existing = db.query(Application).filter(Application.job_id == job_id, Application.worker_user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Anda sudah melamar lowongan ini.")

    application = Application(
        job_id=job.id,
        worker_user_id=user.id,
        status=ApplicationStatus.APPLIED
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.get("/worker/applications", response_model=List[ApplicationResponse])
def get_my_applications(nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    if user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Hanya role WORKER yang dapat melihat lamaran.")
    return db.query(Application).filter(Application.worker_user_id == user.id).all()

# --- Owner Melihat Daftar Pelamar di Lowongannya ---
@router.get("/jobs/{job_id}/applications", response_model=List[ApplicationResponse])
def list_job_applications(job_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan.")
    
    business = db.query(Business).filter(Business.id == job.business_id).first()
    if not business or business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak. Anda bukan pemilik bisnis ini.")

    return db.query(Application).filter(Application.job_id == job_id).all()

# --- Owner Menerima Lamaran & Menjadikan Worker sebagai Staff ---
@router.patch("/applications/{application_id}/accept", status_code=status.HTTP_200_OK)
def accept_application(application_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan.")
    
    job = db.query(Job).filter(Job.id == application.job_id).first()
    business = db.query(Business).filter(Business.id == job.business_id).first()
    
    if not business or business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    application.status = ApplicationStatus.ACCEPTED

    existing_employee = db.query(Employee).filter(
        Employee.business_id == business.id,
        Employee.worker_user_id == application.worker_user_id
    ).first()

    if not existing_employee:
        new_employee = Employee(
            business_id=business.id,
            worker_user_id=application.worker_user_id,
            position=job.title,
            start_date="2026-10-19",
            status=EmployeeStatus.ACTIVE
        )
        db.add(new_employee)

    db.commit()
    return {"message": "Lamaran berhasil diterima! Pekerja resmi terikat sebagai staff operasional usaha Anda."}

# --- BARU: Owner Membuat Rekam Kerja Berbasis Email ---
class WorkRecordCreatePayload(BaseModel):
    title: str
    tasks: str
    skills: str
    start_date: str
    end_date: Optional[str] = None
    worker_email: Optional[EmailStr] = None

@router.post("/businesses/{business_id}/work-records", status_code=status.HTTP_201_CREATED)
def create_work_record(business_id: int, payload: WorkRecordCreatePayload, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    business = db.query(Business).filter(Business.id == business_id).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Bisnis tidak ditemukan.")

    if business.owner_user_id != user.id or user.role != UserRole.EMPLOYER_OWNER:
        raise HTTPException(status_code=403, detail="Hanya Pemilik Usaha (Owner) yang berhak membuat rekam kerja.")

    worker_user_id = None
    if payload.worker_email:
        clean_email = payload.worker_email.strip().lower()
        worker_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
        if not worker_user:
            raise HTTPException(status_code=404, detail=f"User dengan email '{payload.worker_email}' tidak ditemukan di sistem.")
        worker_user_id = worker_user.id
        
        # Otomatis daftarkan ke tabel employees jika belum terikat
        existing_emp = db.query(Employee).filter(
            Employee.business_id == business.id, 
            Employee.worker_user_id == worker_user_id
        ).first()
        if not existing_emp:
            new_emp = Employee(
                business_id=business.id,
                worker_user_id=worker_user_id,
                position=payload.title,
                start_date=payload.start_date,
                status=EmployeeStatus.ACTIVE
            )
            db.add(new_emp)

    work_record = WorkRecord(
        business_id=business.id,
        title=payload.title,
        tasks=payload.tasks,
        skills=payload.skills,
        start_date=payload.start_date,
        end_date=payload.end_date,
        worker_user_id=worker_user_id,
        is_verified=False,
        verification_status=VerificationStatus.PENDING
    )
    db.add(work_record)
    db.commit()
    db.refresh(work_record)
    
    return {"message": "Rekam kerja berhasil dibuat dan terhubung ke staff!", "record_id": work_record.id}

# --- BARU: Verifikasi Rekam Kerja Berbasis Email ---
class VerifyRecordByEmailPayload(BaseModel):
    worker_email: EmailStr

@router.patch("/work-records/verify-by-email", status_code=status.HTTP_200_OK)
def verify_work_record_by_email(payload: VerifyRecordByEmailPayload, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    if user.role != UserRole.EMPLOYER_OWNER:
        raise HTTPException(status_code=403, detail="Hanya owner yang dapat memverifikasi rekam kerja.")
    
    clean_email = payload.worker_email.strip().lower()

    target_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User dengan email '{payload.worker_email}' tidak terdaftar di sistem.")

    records = db.query(WorkRecord).filter(WorkRecord.worker_user_id == target_user.id).all()
    if not records:
        raise HTTPException(
            status_code=404, 
            detail=f"Email terdaftar, tetapi Owner belum membuat Rekam Kerja (Work Record) untuk pekerja ini. Silakan buat rekam kerja terlebih dahulu."
        )

    for rec in records:
        rec.is_verified = True

    db.commit()
    return {"message": f"Semua rekam kerja untuk email {payload.worker_email} berhasil diverifikasi sah!"}

@router.get("/work-passport/me")
def get_my_work_passport(nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    if user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Hanya role WORKER yang memiliki Work Passport.")

    records = db.query(WorkRecord).filter(WorkRecord.worker_user_id == user.id).all()
    
    verified_records = []
    unverified_records = []

    for rec in records:
        data = {
            "id": rec.id,
            "title": rec.title,
            "tasks": rec.tasks,
            "skills": rec.skills,
            "start_date": rec.start_date,
            "end_date": rec.end_date,
            "verification_status": rec.verification_status
        }
        if rec.verification_status == VerificationStatus.VERIFIED or rec.is_verified:
            verified_records.append(data)
        else:
            unverified_records.append(data)

    return {
        "worker_user_id": user.id,
        "verified_experiences": verified_records,
        "pending_or_unverified_experiences": unverified_records,
        "disclaimer": "Catatan yang ditampilkan terbagi berdasarkan status verifikasi pemberi kerja."
    }

# --- AI / Transparent Job Matching Explanation ---
@router.get("/jobs/{job_id}/matches")
def explain_job_matches(job_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan.")

    business = db.query(Business).filter(Business.id == job.business_id).first()
    if not business or business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Hanya pemilik bisnis yang dapat melihat analisis kecocokan kandidat.")

    applications = db.query(Application).filter(Application.job_id == job_id).all()
    results = []

    for app in applications:
        worker_profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == app.worker_user_id).first()
        worker_skills = db.query(WorkerSkill).filter(WorkerSkill.worker_user_id == app.worker_user_id).all()
        skill_ids = [ws.skill_id for ws in worker_skills]
        skills_names = [s.name for s in db.query(Skill).filter(Skill.id.in_(skill_ids)).all()] if skill_ids else []

        match_score = 50
        matching_factors = []
        missing_factors = []

        if worker_profile and worker_profile.location.lower() in job.location.lower():
            match_score += 25
            matching_factors.append("Lokasi sesuai dengan lowongan.")
        else:
            missing_factors.append("Lokasi berbeda.")

        if len(skills_names) > 0:
            match_score += 25
            matching_factors.append(f"Memiliki keterampilan terdaftar: {', '.join(skills_names)}")
        else:
            missing_factors.append("Belum mencantumkan keterampilan.")

        results.append({
            "application_id": app.id,
            "worker_user_id": app.worker_user_id,
            "worker_name": worker_profile.display_name if worker_profile else "Tanpa Nama",
            "match_score": match_score,
            "matching_factors": matching_factors,
            "missing_factors": missing_factors,
            "status": app.status
        })

    return {"job_id": job.id, "job_title": job.title, "candidates_analysis": results}