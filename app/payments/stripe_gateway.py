from typing import Dict, Any
from .gateway import PaymentGatewayInterface
from ..config.settings import settings

# Stripe gateway stub: shows where to put real keys and webhook handling.
# Uses environment vars: STRIPE_SECRET, STRIPE_WEBHOOK_SECRET

class StripeGateway(PaymentGatewayInterface):
    def __init__(self):
        self.secret = settings.STRIPE_SECRET
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def create_payment(self, amount: float, currency: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # In production: call stripe.checkout.Session.create(...)
        # This is a stub to illustrate integration.
        return {'id': 'stripe_stub_123', 'status': 'created', 'checkout_url': 'https://stripe.com/checkout-session'}

    def handle_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        # Validate signature using self.webhook_secret, then parse event
        # This stub simply returns a fake success event
        return {'type': 'payment_success', 'id': 'stripe_stub_123'}
