from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from decimal import Decimal
from typing import List
import secrets
import string

from app.core.database import get_db
from app.core.security import hash_token
from app.auth.models import User, Session as UserSession, UserRole
from app.businesses.models import Business, Product, Sale, SaleItem, BusinessCost
from app.workforce.models import Employee, EmployeeStatus
from app.businesses.schemas import (
    BusinessCreate, BusinessUpdate, BusinessResponse,
    ProductCreate, ProductResponse, SaleCreate, CostCreate
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/businesses", tags=["Business Core"])

def generate_secure_business_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    code_part = "".join(secrets.choice(alphabet) for _ in range(6))
    return f"NUSA-{code_part}"

def get_current_user_and_business(business_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)) -> tuple[User, Business]:
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan.")
    
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    if not session_record:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User tidak ditemukan.")
    
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Bisnis tidak ditemukan.")
    
    is_owner = business.owner_user_id == user.id
    is_staff = False
    
    if user.role == UserRole.EMPLOYER_STAFF:
        employee_record = db.query(Employee).filter(
            Employee.worker_user_id == user.id,
            Employee.business_id == business.id
        ).first()
        if employee_record:
            is_staff = True

    if not (is_owner or is_staff or user.role == UserRole.EMPLOYER_OWNER):
        raise HTTPException(status_code=403, detail="Akses ditolak ke bisnis ini.")
        
    return user, business

@router.post("", status_code=status.HTTP_201_CREATED, response_model=BusinessResponse)
def create_business(payload: BusinessCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan.")
    
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    if not session_record:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    
    user = db.query(User).filter(User.id == session_record.user_id).first()
    
    if user.role != UserRole.EMPLOYER_OWNER:
        raise HTTPException(status_code=403, detail="Hanya role EMPLOYER_OWNER yang dapat membuat profil bisnis.")

    existing_business = db.query(Business).filter(Business.owner_user_id == user.id).first()
    if existing_business:
        raise HTTPException(status_code=400, detail="Anda sudah memiliki profil bisnis terdaftar.")

    # Generate Kode Unik Toko Anti-Manipulasi
    unique_code = generate_secure_business_code()
    while db.query(Business).filter(Business.business_code == unique_code).first():
        unique_code = generate_secure_business_code()

    new_business = Business(
        name=payload.name,
        category=payload.category,
        location=payload.location,
        owner_user_id=user.id,
        business_code=unique_code
    )
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    return new_business

class ConnectStaffPayload(BaseModel):
    business_code: str

@router.post("/connect-staff", status_code=200)
def connect_staff_to_business(payload: ConnectStaffPayload, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan.")
    
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    if not session_record:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user or user.role != UserRole.EMPLOYER_STAFF:
        raise HTTPException(status_code=403, detail="Hanya staff operasional yang dapat menautkan akun.")
    
    business = db.query(Business).filter(Business.business_code == payload.business_code.strip().upper()).first()
    if not business:
        raise HTTPException(status_code=404, detail="Kode Unik Toko tidak valid atau tidak ditemukan.")

    existing = db.query(Employee).filter(
        Employee.business_id == business.id,
        Employee.worker_user_id == user.id
    ).first()

    if not existing:
        new_emp = Employee(
            business_id=business.id,
            worker_user_id=user.id,
            position="Staff Operasional",
            start_date="2026-10-19",
            status=EmployeeStatus.ACTIVE
        )
        db.add(new_emp)
        db.commit()

    return {"message": f"Berhasil terhubung ke toko {business.name}!"}

@router.get("/me/active", response_model=BusinessResponse)
def get_my_active_business(nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    if not nusa_session:
        raise HTTPException(status_code=401, detail="Sesi tidak ditemukan.")
    
    token_hash_val = hash_token(nusa_session)
    session_record = db.query(UserSession).filter(UserSession.token_hash == token_hash_val).first()
    if not session_record:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User tidak ditemukan.")
    
    if user.role == UserRole.EMPLOYER_OWNER:
        business = db.query(Business).filter(Business.owner_user_id == user.id).first()
        if not business:
            raise HTTPException(status_code=404, detail="Anda belum memiliki profil bisnis.")
        return business
        
    elif user.role == UserRole.EMPLOYER_STAFF:
        employee_record = db.query(Employee).filter(Employee.worker_user_id == user.id).first()
        if employee_record:
            business = db.query(Business).filter(Business.id == employee_record.business_id).first()
            if business:
                return business
        
        raise HTTPException(status_code=404, detail="Akun staff belum terikat ke bisnis manapun.")

    raise HTTPException(status_code=403, detail="Akses tidak sah.")

@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(business_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_current_user_and_business(business_id, nusa_session, db)
    return business

@router.post("/{business_id}/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_product(business_id: int, payload: ProductCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_current_user_and_business(business_id, nusa_session, db)
    
    product = Product(
        business_id=business.id,
        name=payload.name,
        price=payload.price
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{business_id}/products", response_model=List[ProductResponse])
def list_products(business_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_current_user_and_business(business_id, nusa_session, db)
    return business.products

@router.post("/{business_id}/sales", status_code=status.HTTP_201_CREATED)
def create_sale(business_id: int, payload: SaleCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_current_user_and_business(business_id, nusa_session, db)
    
    total_sale_amount = Decimal("0.00")
    sale_items_data = []

    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.business_id == business.id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produk dengan ID {item.product_id} tidak ditemukan.")
        
        line_total = product.price * item.quantity
        total_sale_amount += line_total
        
        sale_items_data.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "unit_price": product.price,
            "line_total": line_total
        })

    new_sale = Sale(
        business_id=business.id,
        total_amount=total_sale_amount,
        notes=payload.notes
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    for item_data in sale_items_data:
        sale_item = SaleItem(
            sale_id=new_sale.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            line_total=item_data["line_total"]
        )
        db.add(sale_item)
    db.commit()

    return {"message": "Transaksi penjualan berhasil dicatat", "sale_id": new_sale.id, "total_amount": total_sale_amount}

@router.post("/{business_id}/costs", status_code=status.HTTP_201_CREATED)
def create_cost(business_id: int, payload: CostCreate, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_current_user_and_business(business_id, nusa_session, db)
    
    cost = BusinessCost(
        business_id=business.id,
        category=payload.category,
        amount=payload.amount,
        description=payload.description
    )
    db.add(cost)
    db.commit()
    db.refresh(cost)
    return {"message": "Catatan biaya berhasil disimpan", "cost_id": cost.id}

@router.get("/{business_id}/dashboard")
def get_business_dashboard(business_id: int, nusa_session: str = Cookie(None), db: DBSession = Depends(get_db)):
    _, business = get_current_user_and_business(business_id, nusa_session, db)
    
    total_turnover = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(Sale.business_id == business.id).scalar()
    total_transactions = db.query(func.count(Sale.id)).filter(Sale.business_id == business.id).scalar()
    total_costs = db.query(func.coalesce(func.sum(BusinessCost.amount), 0)).filter(BusinessCost.business_id == business.id).scalar()
    estimated_net = total_turnover - total_costs

    return {
        "business_name": business.name,
        "total_omzet": total_turnover,
        "total_transactions": total_transactions,
        "total_costs": total_costs,
        "estimated_business_result": estimated_net,
        "disclaimer": "Angka ini adalah estimasi hasil usaha berdasarkan data biaya yang tercatat, bukan laba akuntansi resmi."
    }