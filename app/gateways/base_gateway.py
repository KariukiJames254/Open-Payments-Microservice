from abc import ABC, abstractmethod
from typing import Any, Dict

class PaymentGateway(ABC):
    """
    Base interface for payment gateways.
    All implementing gateways must provide concrete implementations for these methods.
    """

    @abstractmethod
    async def initiate_payment(self, transaction_id: str, amount: float, currency: str, phone: str) -> Dict[str, Any]:
        """
        Initiates a payment request to the external provider.
        """
        pass

    @abstractmethod
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Checks the status of a specific transaction asynchronously.
        """
        pass

    @abstractmethod
    async def handle_callback(self, payload: dict) -> Dict[str, Any]:
        """
        Parses the provider's webhook payload and returns normalized status / identifiers.
        """
        pass
