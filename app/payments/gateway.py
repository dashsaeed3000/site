from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentGatewayInterface(ABC):
    @abstractmethod
    def create_payment(self, amount: float, currency: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def handle_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        pass
