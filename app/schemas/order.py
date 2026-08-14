from pydantic import BaseModel
from datetime import datetime

class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CheckoutResponse(BaseModel):
    order: OrderOut
    client_secret: str