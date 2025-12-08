from flask import Blueprint, request, jsonify
from ..payments.mock_gateway import MockGateway
from ..payments.stripe_gateway import StripeGateway
from ..config.settings import settings

payments_bp = Blueprint('payments', __name__)

# choose gateway based on env or use mock
_gateway = StripeGateway() if settings.STRIPE_SECRET else MockGateway()

@payments_bp.route('/create', methods=['POST'])
def create_payment():
    data = request.json or {}
    amount = data.get('amount')
    currency = data.get('currency', 'usd')
    metadata = data.get('metadata', {})
    result = _gateway.create_payment(amount, currency, metadata)
    return jsonify(result)

@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    headers = {k: v for k, v in request.headers.items()}
    result = _gateway.handle_webhook(payload, headers)
    # In production map result to order state transitions
    return jsonify(result)
