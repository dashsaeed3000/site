from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, flash
from pathlib import Path
from ..config.settings import settings
from ..repositories.db import get_session
from ..services.product_service import ProductService
from ..services.site_content_service import SiteContentService
from ..services.comment_service import CommentService
from ..utils.upload import get_upload_folder

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    with next(get_session()) as db:
        svc = ProductService(db)
        products = svc.list_products()
        
        # Eagerly load category relationships to avoid detached instance errors
        # Access category for each product while session is still open
        for product in products:
            _ = product.category  # Trigger eager load
        
        # Get site content
        content_svc = SiteContentService(db)
        site_content = content_svc.get_all_content()
        
        # Parse JSON data for sections that need it
        sliders = []
        testimonials = []
        services = []
        
        # Get slider items
        slider_items = content_svc.get_content_list('slider_')
        for item in slider_items:
            sliders.append({
                'title': item.Title,
                'content': item.Content,
                'image': item.ImageUrl,
                'link': item.LinkUrl,
                'link_text': item.LinkText,
            })
        
        # Get testimonial items
        testimonial_items = content_svc.get_content_list('testimonial_')
        for item in testimonial_items:
            testimonials.append({
                'text': item.Content,
                'author': item.Field1,  # Author name
                'role': item.Field2,     # Author role
                'image': item.ImageUrl,
            })
        
        # Get service items
        service_items = content_svc.get_content_list('service_')
        for item in service_items:
            services.append({
                'title': item.Title,
                'content': item.Content,
                'image': item.ImageUrl,
                'number': item.Field1,  # Service number
            })
        
        # Convert products to list to detach from session properly
        products_list = list(products)
    
    return render_template('index.html', 
                         products=products_list,
                         site_content=site_content,
                         sliders=sliders,
                         testimonials=testimonials,
                         services=services)

@main_bp.route('/product/<slug>', methods=['GET', 'POST'])
def product_detail(slug):
    with next(get_session()) as db:
        svc = ProductService(db)
        product = svc.get_product(slug)
        if not product:
            return "Product not found", 404
        
        # Eagerly load images and category while session is open
        _ = product.images  # Trigger eager load
        _ = product.category  # Trigger eager load
        # Convert to list to detach from session
        images_list = list(product.images) if product.images else []
    
    # Handle comment submission
    if request.method == 'POST' and 'comment_body' in request.form:
        comment_body = request.form.get('comment_body', '').strip()
        parent_id = request.form.get('parent_id') or None
        rating = request.form.get('rating')
        rating = int(rating) if rating and rating.isdigit() else None
        
        if comment_body:
            with next(get_session()) as db:
                comment_svc = CommentService(db)
                try:
                    comment_svc.create_comment(
                        product_id=product.Id,
                        body=comment_body,
                        parent_id=parent_id,
                        user_id=None,  # Can be set if user is logged in
                        rating=rating
                    )
                    flash('نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.', 'success')
                except Exception as e:
                    flash('خطا در ثبت نظر. لطفا دوباره تلاش کنید.', 'error')
            return redirect(url_for('main.product_detail', slug=slug))
    
    # Load approved comments
    comments = []
    try:
        with next(get_session()) as db:
            comment_svc = CommentService(db)
            comments = comment_svc.get_product_comments(product.Id, approved_only=True)
            # Load replies for each comment
            for comment in comments:
                comment.replies_list = comment_svc.get_comment_replies(comment.Id, approved_only=True)
    except Exception:
        comments = []
    
    return render_template('product_detail.html', product=product, comments=comments)

@main_bp.route('/post')
@main_bp.route('/post/<slug>')
def post(slug=None):
    return render_template('post.html')

@main_bp.route('/search')
def search():
    """Search products"""
    query = request.args.get('q', '').strip()
    products = []
    
    if query:
        with next(get_session()) as db:
            svc = ProductService(db)
            products = svc.search_products(query)
            # Eagerly load category relationships to avoid detached instance errors
            for product in products:
                _ = product.category  # Trigger eager load
            # Convert to list to detach from session properly
            products = list(products)
    
    return render_template('search_results.html', 
                         products=products, 
                         query=query)

@main_bp.route('/cart')
def cart():
    return render_template('project.html')

@main_bp.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = Path(get_upload_folder())
    # Ensure the file exists
    file_path = upload_folder / filename
    if file_path.exists():
        return send_from_directory(str(upload_folder), filename)
    return "File not found", 404
