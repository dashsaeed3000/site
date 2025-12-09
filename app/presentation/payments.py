from flask import Blueprint, request, jsonify, session, redirect, url_for
from ..payments.mock_gateway import MockGateway
from ..payments.stripe_gateway import StripeGateway
from ..config.settings import settings
from ..repositories.db import get_session
from ..services.order_service import OrderService

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
    """Handle payment webhook and create order"""
    payload = request.get_data()
    headers = dict(request.headers)
    
    # Process webhook
    event = _gateway.handle_webhook(payload, headers)
    
    # If payment successful, update order
    if event.get('type') == 'payment_success':
        transaction_id = event.get('id', '')
        order_id = event.get('metadata', {}).get('order_id')
        
        if order_id:
            with next(get_session()) as db:
                order_service = OrderService(db)
                try:
                    order = order_service.update_order_payment(
                        order_id=order_id,
                        transaction_id=transaction_id,
                        payment_method=event.get('payment_method', 'unknown')
                    )
                    if order:
                        db.commit()
                        return jsonify({'status': 'success', 'order_number': order.OrderNumber})
                except Exception as e:
                    db.rollback()
                    return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'received'})
    headers = {k: v for k, v in request.headers.items()}
    result = _gateway.handle_webhook(payload, headers)
    # In production map result to order state transitions
    return jsonify(result)
