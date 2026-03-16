from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, condecimal

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    amount: condecimal(gt=0, max_digits=10, decimal_places=2) = Field(
        ..., json_schema_extra={"example": 1500}
    )
    currency: str = Field(default="KES", max_length=3, json_schema_extra={"example": "KES"})
    customer_phone: str = Field(..., max_length=20, json_schema_extra={"example": "254700000000"})


class PaymentResponse(BaseModel):
    id: UUID
    transaction_id: str
    amount: condecimal(max_digits=10, decimal_places=2)
    currency: str
    customer_phone: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus
    gateway_response: Optional[dict] = None
