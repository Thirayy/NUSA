from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import hash_token
from app.auth.models import User, Session as UserSession, UserRole
from app.businesses.models import Business, Sale, BusinessCost
from app.ai.provider import ai_provider

router = APIRouter(prefix="/api/v1/businesses/{business_id}/ai", tags=["AI Services"])

def get_verified_business_owner(business_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)) -> tuple[User, Business]:
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan.")
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    if not session_record:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    
    user = db.query(User).filter(User.id == session_record.user_id).first()
    business = db.query(Business).filter(Business.id == business_id).first()
    
    if not business or business.owner_user_id != user.id or user.role != UserRole.EMPLOYER_OWNER:
        raise HTTPException(status_code=403, detail="Akses eksklusif Pemilik Usaha (Owner) diperlukan untuk Decision Room.")
        
    return user, business

@router.post("/decision-room")
def ai_decision_room(business_id: int, payload: dict, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_verified_business_owner(business_id, nusa_session, db)
    user_question = payload.get("question", "Bagaimana kondisi bisnis saya?")

    # Ambil metrik deterministik langsung dari database backend
    total_turnover = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(Sale.business_id == business.id).scalar()
    total_transactions = db.query(func.count(Sale.id)).filter(Sale.business_id == business.id).scalar()
    total_costs = db.query(func.coalesce(func.sum(BusinessCost.amount), 0)).filter(BusinessCost.business_id == business.id).scalar()
    estimated_net = total_turnover - total_costs

    system_prompt = (
        "Anda adalah AI Business Analyst untuk NUSA — AI Business & Workforce Ecosystem. "
        "Tugas Anda adalah menganalisis data bisnis yang dihitung secara deterministik oleh backend. "
        "Pisahkan fakta dari asumsi. Jangan mengarang angka. Sediakan ringkasan kondisi, kemungkinan penyebab, "
        "beberapa alternatif tindakan, manfaat/risiko, dan catatan keterbatasan data. Keputusan akhir ada pada manusia."
    )

    context_message = (
        f"Data Bisnis '{business.name}' ({business.category} di {business.location}):\n"
        f"- Total Omzet: Rp {total_turnover}\n"
        f"- Jumlah Transaksi: {total_transactions}\n"
        f"- Total Biaya Tercatat: Rp {total_costs}\n"
        f"- Estimasi Hasil Usaha: Rp {estimated_net}\n\n"
        f"Pertanyaan Pengguna: {user_question}"
    )

    ai_analysis = ai_provider.generate_chat_response(system_prompt, context_message)

    return {
        "business_name": business.name,
        "metrics_used": {
            "total_omzet": float(total_turnover),
            "total_transactions": total_transactions,
            "total_costs": float(total_costs),
            "estimated_business_result": float(estimated_net)
        },
        "ai_analysis": ai_analysis,
        "disclaimer": "Analisis ini dihasilkan oleh AI berdasarkan data backend terverifikasi dan merupakan estimasi operasional."
    }