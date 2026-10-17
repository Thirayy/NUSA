from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session as DBSession
from typing import List

from app.core.database import get_db
from app.core.security import hash_token
from app.auth.models import User, Session as UserSession, UserRole
from app.businesses.models import Business
from app.workforce.models import WorkerProfile, Job, Application, JobStatus, ApplicationStatus, WorkerSkill, Skill
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

# --- Lowongan Kerja (Jobs) oleh Employer ---
@router.post("/businesses/{business_id}/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(business_id: int, payload: JobCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business or business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak ke bisnis ini.")

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

    # Cegah lamaran ganda[cite: 4]
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

# --- AI / Transparent Job Matching Explanation ---
@router.get("/jobs/{job_id}/matches")
def explain_job_matches(job_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan.")

    business = db.query(Business).filter(Business.id == job.business_id).first()
    if business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Hanya pemilik bisnis yang dapat melihat analisis kecocokan kandidat.")

    applications = db.query(Application).filter(Application.job_id == job_id).all()
    results = []

    for app in applications:
        worker_profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == app.worker_user_id).first()
        worker_skills = db.query(WorkerSkill).filter(WorkerSkill.worker_user_id == app.worker_user_id).all()
        skill_ids = [ws.skill_id for ws in worker_skills]
        skills_names = [s.name for s in db.query(Skill).filter(Skill.id.in_(skill_ids)).all()] if skill_ids else []

        # Aturan matching transparan sederhana berdasarkan lokasi & keterampilan[cite: 4]
        match_score = 50 # Baseline
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