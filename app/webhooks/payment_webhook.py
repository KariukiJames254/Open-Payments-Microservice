from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

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
    raw_payload = await request.body()
    
    if not verify_webhook_signature(raw_payload, signature):
        raise HTTPException(status_code=400, detail="Invalid Webhook Signature")

    import json
    payload = json.loads(raw_payload.decode("utf-8"))
    
    # Process webhook using the service layer
    await service.process_webhook(payload)
    
    return {"status": "received"}
