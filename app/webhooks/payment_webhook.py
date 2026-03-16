from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import json
import logging

from app.services.payment_service import PaymentService
from app.gateways.mpesa_gateway import MpesaGateway
from app.core.database import get_db
from app.webhooks.verify import verify_webhook_signature
from app.core.rate_limiter import limiter

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)

def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    gateway = MpesaGateway() 
    return PaymentService(db, gateway)


@router.post("/payment")
@limiter.limit("60/minute")
async def payment_webhook(
    request: Request,
    signature: Optional[str] = Header(None, alias="X-Signature"),
    service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Receives callbacks from payment gateways and updates payment status.
    """
    # 1. Read the raw body
    body_bytes = await request.body()
    
    if not body_bytes:
        raise HTTPException(status_code=400, detail="Request body is empty")

    # 2. Verify signature BEFORE parsing (security first)
    if not verify_webhook_signature(body_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid Webhook Signature")

    # 3. Parse JSON safely
    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # 4. Process webhook
    await service.process_webhook(payload)
    
    return {"status": "received"}
