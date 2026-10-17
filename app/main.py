from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db, Base, engine
from app.core.config import settings
from app.auth.router import router as auth_router
from app.businesses.router import router as business_router
from app.workforce.router import router as workforce_router
from app.work_records.router import router as work_records_router
from app.ai.router import router as ai_router
from fastapi.middleware.cors import CORSMiddleware


# Buat tabel jika belum ada
Base.metadata.create_all(bind=engine)

# Safety check untuk development: tambahkan kolom jika tabel sudah terlanjur ada tapi belum punya kolom tersebut
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR;"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"))

app = FastAPI(
    title="NUSA API",
    description="AI Business & Workforce Ecosystem API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(business_router)
app.include_router(workforce_router)
app.include_router(work_records_router)
app.include_router(ai_router)

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "database": db_status
    }