from typing import Dict, Any
from .gateway import PaymentGatewayInterface

class MockGateway(PaymentGatewayInterface):
    def create_payment(self, amount: float, currency: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # returns a fake checkout URL and id
        return {'id': 'mock_pay_123', 'status': 'created', 'checkout_url': 'https://example.com/mock-checkout'}

    def handle_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        # parse payload as needed in real gateway
        return {'type': 'payment_success', 'id': 'mock_pay_123'}
