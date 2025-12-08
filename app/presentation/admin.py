from flask import Blueprint, render_template, request, redirect, url_for
from ..repositories.db import get_session
from ..services.product_service import ProductService

admin_bp = Blueprint('admin_products', __name__)

@admin_bp.route('/')
def admin_index():
    with next(get_session()) as db:
        svc = ProductService(db)
        products = svc.list_products()
    return render_template('services.html', products=products)

@admin_bp.route('/product/new', methods=['GET','POST'])
def product_new():
    if request.method == 'POST':
        data = {k: request.form.get(k) for k in ['name','slug','description','price','image']}
        with next(get_session()) as db:
            svc = ProductService(db)
            svc.create_product(name=data['name'], slug=data['slug'], description=data['description'], price=data['price'], image=data['image'])
        return redirect(url_for('admin_products.admin_index'))
    return render_template('project.html')
