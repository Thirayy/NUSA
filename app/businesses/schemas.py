from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class BusinessCreate(BaseModel):
    name: str
    category: str
    location: str

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None

class BusinessResponse(BaseModel):
    id: int
    name: str
    category: str
    location: str
    owner_user_id: int
    business_code: str  # <-- Tambahkan ini agar kode unik muncul di dashboard owner

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    price: Decimal

class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    is_active: int

    class Config:
        from_attributes = True

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int

class SaleCreate(BaseModel):
    notes: Optional[str] = None
    items: List[SaleItemCreate]

class CostCreate(BaseModel):
    category: str
    amount: Decimal
    description: Optional[str] = None