from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone
from typing import List

from app.core.database import get_db
from app.core.security import hash_token
from app.auth.models import User, Session as UserSession, UserRole
from app.businesses.models import Business
from app.work_records.models import WorkRecord, WorkRecordClaim, VerificationStatus
from app.work_records.schemas import WorkRecordCreate, WorkRecordResponse, CorrectionRequestCreate

router = APIRouter(prefix="/api/v1", tags=["Work Records & Passport"])

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

# --- Employer: Membuat Work Record ---
@router.post("/businesses/{business_id}/work-records", response_model=WorkRecordResponse, status_code=status.HTTP_201_CREATED)
def create_work_record(business_id: int, payload: WorkRecordCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business or business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak ke bisnis ini.")

    record = WorkRecord(
        business_id=business.id,
        worker_user_id=payload.worker_user_id,
        title=payload.title,
        tasks=payload.tasks,
        skills=payload.skills,
        start_date=payload.start_date,
        end_date=payload.end_date,
        verification_status=VerificationStatus.PENDING
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# --- Employer: Verifikasi Work Record ---
@router.patch("/work-records/{work_record_id}/verify")
def verify_work_record(work_record_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    record = db.query(WorkRecord).filter(WorkRecord.id == work_record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Work Record tidak ditemukan.")

    business = db.query(Business).filter(Business.id == record.business_id).first()
    if business.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Hanya pemilik bisnis yang dapat memverifikasi catatan.")

    record.verification_status = VerificationStatus.VERIFIED
    record.verified_by_user_id = user.id
    record.verified_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Work Record berhasil diverifikasi dan sah masuk ke Work Passport.", "record_id": record.id}

# --- Worker: Mengklaim Work Record ---
@router.post("/work-records/{work_record_id}/claim", status_code=status.HTTP_201_CREATED)
def claim_work_record(work_record_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    if user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Hanya role WORKER yang dapat mengklaim rekam kerja.")

    record = db.query(WorkRecord).filter(WorkRecord.id == work_record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Work Record tidak ditemukan.")

    # Cek klaim ganda
    existing_claim = db.query(WorkRecordClaim).filter(WorkRecordClaim.work_record_id == record.id, WorkRecordClaim.worker_user_id == user.id).first()
    if existing_claim:
        raise HTTPException(status_code=400, detail="Anda sudah mengajukan klaim untuk catatan ini.")

    claim = WorkRecordClaim(
        work_record_id=record.id,
        worker_user_id=user.id,
        status="APPROVED" # Otomatis disetujui atau pending sesuai alur verifikasi aman[cite: 6]
    )
    record.worker_user_id = user.id # Tautkan ke akun worker
    db.add(claim)
    db.commit()

    return {"message": "Work Record berhasil diklaim dan ditautkan ke akun Anda."}

# --- Worker: Melihat Work Passport Miliknya ---
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
        if rec.verification_status == VerificationStatus.VERIFIED:
            verified_records.append(data)
        else:
            unverified_records.append(data)

    return {
        "worker_user_id": user.id,
        "verified_experiences": verified_records,
        "pending_or_unverified_experiences": unverified_records,
        "disclaimer": "Catatan yang ditampilkan terbagi berdasarkan status verifikasi pemberi kerja[cite: 6]."
    }

# --- Worker: Meminta Koreksi Catatan ---
@router.post("/work-records/{work_record_id}/correction-requests")
def request_work_record_correction(work_record_id: int, payload: CorrectionRequestCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    user = get_current_user_from_cookie(nusa_session, db)
    record = db.query(WorkRecord).filter(WorkRecord.id == work_record_id, WorkRecord.worker_user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Work Record tidak ditemukan atau tidak terkait dengan Anda.")

    record.verification_status = VerificationStatus.DISPUTED
    db.commit()

    return {"message": "Permintaan koreksi berhasil dikirim ke pemberi kerja. Status catatan diubah menjadi DISPUTED."}