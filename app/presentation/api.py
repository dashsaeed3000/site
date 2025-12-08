from flask import Blueprint, jsonify, request
from ..repositories.db import get_session
from ..services.product_service import ProductService

api_bp = Blueprint('api', __name__)

@api_bp.route('/products', methods=['GET'])
def list_products():
    with next(get_session()) as db:
        svc = ProductService(db)
        products = svc.list_products()
        data = [
            {'id': p.id, 'name': p.name, 'slug': p.slug, 'price': float(p.price), 'description': p.description}
            for p in products
        ]
        return jsonify({'products': data})

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    with next(get_session()) as db:
        svc = ProductService(db)
        p = svc.repo.get_by_id(product_id)
        if not p:
            return jsonify({'error': 'not found'}), 404
        return jsonify({'id': p.id, 'name': p.name, 'slug': p.slug, 'price': float(p.price)})
