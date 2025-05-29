from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    group: str  # 'Administrador' o 'Lectura'

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    group: Optional[str] = None

class UserResponse(UserBase):
    id: int
    groups: List[str]
    
    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    cost: Optional[float] = None
    sale_price: Optional[float] = None
    active: Optional[bool] = None

class StockMovement(BaseModel):
    quantity: int
    order_id: Optional[str] = None
    notes: Optional[str] = None

class StockUpdate(BaseModel):
    quantity: int
    
class ProductMovementResponse(BaseModel):
    movement_id: str
    date: datetime
    product_id: str
    movement_type: str
    quantity: int
    order_id: Optional[str]
    current_stock: int 
    
    class Config:
        from_attributes = True 