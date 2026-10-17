from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import hash_password, verify_password, generate_session_token, hash_token
from app.auth.models import User, Session as UserSession
from app.auth.schemas import UserRegister, UserLogin, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

SESSION_EXPIRE_DAYS = 7

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(payload: UserRegister, db: DBSession = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
    
    hashed_pwd = hash_password(payload.password)
    new_user = User(
        email=payload.email,
        password_hash=hashed_pwd,
        role=payload.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(payload: UserLogin, response: Response, db: DBSession = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah.")
    
    # Buat token sesi
    raw_token = generate_session_token()
    token_hash_val = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRE_DAYS)

    new_session = UserSession(
        user_id=user.id,
        token_hash=token_hash_val,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()

    # Set cookie HttpOnly
    response.set_cookie(
        key="nusa_session",
        value=raw_token,
        httponly=True,
        secure=True,  # Ubah ke True jika menggunakan HTTPS di production
        samesite="lax",
        expires=int(expires_at.timestamp())
    )
    return {"message": "Login berhasil", "role": user.role}

@router.post("/logout")
def logout(response: Response, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    if nusa_session:
        token_hash_val = hash_token(nusa_session)
        db.query(UserSession).filter(UserSession.token_hash == token_hash_val).delete()
        db.commit()
    
    response.delete_cookie("nusa_session")
    return {"message": "Logout berhasil"}

@router.get("/me", response_model=UserResponse)
def get_current_user(nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan atau sudah kedaluwarsa.")
    
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    
    if not session_record or session_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Sesi tidak valid atau sudah kedaluwarsa.")
    
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Pengguna tidak ditemukan.")
    
    return user