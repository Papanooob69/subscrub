from datetime import date
from pydantic import BaseModel
from typing import Literal, Optional


class ToolCreate(BaseModel):
    name: str
    price: float
    billing_cycle: Literal["monthly", "annually"]
    renewal_date: date  # required


class ToolRead(BaseModel):
    id: int
    name: str
    price: float
    billing_cycle: str
    renewal_date: date
    last_used: Optional[date] = None
    owner_id: int

    class Config:
        orm_mode = True


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    billing_cycle: Optional[str] = None
    renewal_date: Optional[date] = None


class ToolUserUsage(BaseModel):
    email: str
    assigned_date: Optional[date]
    last_used: Optional[date]
    status: str
