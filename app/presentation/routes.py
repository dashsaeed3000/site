from flask import Blueprint, render_template, render_template_string, request, redirect, url_for, session, send_from_directory, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from pathlib import Path
from datetime import datetime
from ..config.settings import settings
from ..repositories.db import get_session
from ..services.product_service import ProductService
from ..models.models import Categories, Products
from ..services.site_content_service import SiteContentService
from ..services.comment_service import CommentService
from ..services.cart_service import CartService
from ..services.order_service import OrderService
from ..services.phone_verification_service import PhoneVerificationService
from ..services.user_service import UserService
from ..presentation.forms import RegistrationForm, LoginForm, PhoneVerificationForm, CheckoutForm
from admin_area.models import get_user_by_username
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
        
        # Get service items (legacy site content)
        service_items = content_svc.get_content_list('service_')
        for item in service_items:
            services.append({
                'title': item.Title,
                'content': item.Content,
                'image': item.ImageUrl,
                'number': item.Field1,  # Service number
            })

        # Load parent categories to display in Services section (parent categories only)
        parent_categories = []
        try:
            parents = db.query(Categories).filter(
                Categories.ParentId == None,
                Categories.IsDeleted == False,
                Categories.IsActive == True
            ).order_by(Categories.SortOrder).all()
            for p in parents:
                parent_categories.append({
                    'title': p.Title,
                    'description': p.Description,
                    'slug': p.Slug,
                    'id': p.Id
                })
        except Exception:
            parent_categories = []
        
        # Convert products to list to detach from session properly
        products_list = list(products)
    
    return render_template('index.html', 
                         products=products_list,
                         site_content=site_content,
                         sliders=sliders,
                         testimonials=testimonials,
                         services=services,
                         parent_categories=parent_categories)

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

    # Build reviews summary for template (safe defaults if none)
    reviews = {
        'avg': None,
        'count': 0,
        'items': []
    }
    try:
        # compute average rating from approved top-level comments that have Rating
        ratings = [c.Rating for c in comments if getattr(c, 'Rating', None) is not None]
        if ratings:
            reviews['avg'] = round(sum(ratings) / len(ratings), 1)
        reviews['count'] = len(comments)
        # expose first few comments as review items
        reviews['items'] = comments[:5]
    except Exception:
        reviews = {'avg': None, 'count': 0, 'items': []}

    # Related products (by same category) - safe fallback to empty list
    related = []
    try:
        with next(get_session()) as db:
            if getattr(product, 'CategoryId', None):
                related_q = db.query(Products).filter(
                    Products.CategoryId == product.CategoryId,
                    Products.IsDeleted == False,
                    Products.IsActive == True,
                    Products.Id != product.Id
                ).limit(4).all()
                # convert or attach minimal fields expected by template
                related = list(related_q)
    except Exception:
        related = []

    # category for breadcrumbs (product.category was eager-loaded earlier)
    category = getattr(product, 'category', None)

    return render_template('product_detail.html', product=product, comments=comments, reviews=reviews, related=related, category=category)


@main_bp.route('/category/<slug>')
def category(slug):
    """Show children of a category (parent)"""
    with next(get_session()) as db:
        cat = db.query(Categories).filter(
            Categories.Slug == slug,
            Categories.IsDeleted == False
        ).first()
        if not cat:
            return "دسته مورد نظر یافت نشد", 404

        # Load children (only active, not deleted)
        children = [
            {
                'title': c.Title,
                'description': c.Description,
                'slug': c.Slug,
                'id': c.Id
            }
            for c in cat.children if not c.IsDeleted and c.IsActive
        ]

    return render_template('category_children.html', parent=cat, children=children)

@main_bp.route('/post')
@main_bp.route('/post/<slug>')
def post(slug=None):
    return render_template('post.html')


@main_bp.route('/policy/return')
def return_policy():
        # Minimal placeholder page for return policy
        return render_template_string("""
        {% extends 'base.html' %}
        {% block title %}سیاست بازگشت{% endblock %}
        {% block content %}
        <div class="container" style="padding:40px 0;">
            <h2>سیاست بازگشت</h2>
            <p>اطلاعات بازگشت کالا به زودی اضافه می‌شود. برای پشتیبانی با ما تماس بگیرید.</p>
        </div>
        {% endblock %}
        """)


@main_bp.route('/policy/shipping')
def shipping_info():
        return render_template_string("""
        {% extends 'base.html' %}
        {% block title %}اطلاعات ارسال{% endblock %}
        {% block content %}
        <div class="container" style="padding:40px 0;">
            <h2>اطلاعات ارسال</h2>
            <p>جزئیات زمان و هزینه ارسال به زودی اضافه می‌شود.</p>
        </div>
        {% endblock %}
        """)


@main_bp.route('/policy/privacy')
def privacy():
        return render_template_string("""
        {% extends 'base.html' %}
        {% block title %}حریم خصوصی{% endblock %}
        {% block content %}
        <div class="container" style="padding:40px 0;">
            <h2>حریم خصوصی</h2>
            <p>اطلاعات مربوط به حریم خصوصی کاربران به زودی اضافه می‌شود.</p>
        </div>
        {% endblock %}
        """)

@main_bp.route('/search')
def search():
    """Search products with advanced filters"""
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort_by = request.args.get('sort', 'newest')  # newest, price_low, price_high
    
    products = []
    categories = []
    min_price_db = 0
    max_price_db = 0
    
    with next(get_session()) as db:
        # Get all active categories for filter
        try:
            categories_list = db.query(Categories).filter(
                Categories.IsDeleted == False,
                Categories.IsActive == True,
                Categories.ParentId != None  # Only subcategories
            ).order_by(Categories.Title).all()
            categories = [{'id': c.Id, 'title': c.Title} for c in categories_list]
        except Exception:
            categories = []
        
        # Get price range
        try:
            from sqlalchemy import func
            price_result = db.query(func.min(Product.Price), func.max(Product.Price)).filter(
                Product.IsDeleted == False,
                Product.IsActive == True
            ).first()
            if price_result and price_result[0]:
                min_price_db = int(price_result[0])
                max_price_db = int(price_result[1])
        except Exception:
            pass
        
        # Search and filter products
        if query:
            svc = ProductService(db)
            products = svc.search_products(query)
            
            # Apply category filter
            if category_id:
                products = [p for p in products if p.CategoryId == category_id]
            
            # Apply price filter
            try:
                if min_price and min_price.isdigit():
                    min_p = int(min_price)
                    products = [p for p in products if p.Price and float(p.Price) >= min_p]
                if max_price and max_price.isdigit():
                    max_p = int(max_price)
                    products = [p for p in products if p.Price and float(p.Price) <= max_p]
            except Exception:
                pass
            
            # Eagerly load category relationships
            for product in products:
                _ = product.category
            
            # Sort products
            if sort_by == 'price_low':
                products = sorted(products, key=lambda p: float(p.Price) if p.Price else 0)
            elif sort_by == 'price_high':
                products = sorted(products, key=lambda p: float(p.Price) if p.Price else 0, reverse=True)
            else:  # newest
                products = sorted(products, key=lambda p: p.CreatedAt or datetime.utcnow(), reverse=True)
            
            # Convert to list
            products = list(products)
    
    return render_template('search_results.html', 
                         products=products, 
                         query=query,
                         categories=categories,
                         category_id=category_id,
                         min_price=min_price,
                         max_price=max_price,
                         min_price_db=min_price_db,
                         max_price_db=max_price_db,
                         sort_by=sort_by)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page: reads SiteContent key 'contact' (or 'contact_us') and displays it.
    If not present, renders default contact information. Handles simple contact form POST and flashes a message."""
    from ..services.site_content_service import SiteContentService

    content = None
    data = None
    with next(get_session()) as db:
        sc = SiteContentService(db)
        # try a few common keys
        content = sc.get_content_by_key('contact') or sc.get_content_by_key('contact_us')
        if content:
            data = sc.parse_json_data(content)

    # Fallback defaults
    defaults = {
        'title': getattr(content, 'Title', None) or 'تماس با ما',
        'subtitle': getattr(content, 'Subtitle', None) or 'ما خوشحال می‌شویم از شما بشنویم',
        'content_html': getattr(content, 'Content', None) or (
            '<p>برای ارتباط با ما می‌توانید از روش‌های زیر استفاده کنید یا فرم را پر کنید و پیام خود را ارسال کنید.</p>'
        ),
        'address': getattr(content, 'Field1', None) or 'ایران - مشهد - بلوار سجاد',
        'phone': getattr(content, 'Field2', None) or '+98 203-123-0606',
        'email': getattr(content, 'Field3', None) or 'info@example.com',
        'map_embed': getattr(content, 'Field4', None) or None,
        'image': getattr(content, 'ImageUrl', None) or None,
    }

    # Handle simple contact form submission (no email sent - just flash)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        if not message:
            flash('لطفا پیام خود را بنویسید.', 'error')
            return redirect(url_for('main.contact'))
        # For now, just flash success (could be hooked to send email or save to DB)
        flash('پیام شما ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html', content=content, data=data, defaults=defaults)

@main_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    """Cart page - view and manage cart items"""
    cart_service = CartService()
    
    # Handle POST requests (add to cart from product page)
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        
        if product_id:
            try:
                cart_service.add_item(product_id, quantity)
                flash('محصول به سبد خرید اضافه شد', 'success')
            except Exception as e:
                flash('خطا در افزودن محصول به سبد خرید', 'error')
            return redirect(url_for('main.cart'))
    
    # Get cart items with product details
    cart_items = cart_service.get_cart_with_products()
    cart_total = cart_service.get_cart_total()
    cart_count = cart_service.get_cart_count()
    
    return render_template('cart.html',
                         cart_items=cart_items,
                         cart_total=cart_total,
                         cart_count=cart_count)


@main_bp.route('/cart/add', methods=['POST'])
def cart_add():
    """API endpoint to add item to cart"""
    cart_service = CartService()
    data = request.get_json() or {}
    
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    if not product_id:
        return jsonify({'success': False, 'message': 'شناسه محصول الزامی است'}), 400
    
    try:
        cart_service.add_item(product_id, quantity)
        return jsonify({
            'success': True,
            'message': 'محصول به سبد خرید اضافه شد',
            'cart_count': cart_service.get_cart_count()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@main_bp.route('/cart/update', methods=['POST'])
def cart_update():
    """API endpoint to update cart item quantity"""
    cart_service = CartService()
    data = request.get_json() or {}
    
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    if not product_id:
        return jsonify({'success': False, 'message': 'شناسه محصول الزامی است'}), 400
    
    try:
        cart_service.update_item_quantity(product_id, quantity)
        cart_items = cart_service.get_cart_with_products()
        cart_total = cart_service.get_cart_total()
        return jsonify({
            'success': True,
            'cart_count': cart_service.get_cart_count(),
            'cart_total': cart_total
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@main_bp.route('/cart/remove/<product_id>', methods=['POST'])
def cart_remove(product_id):
    """Remove item from cart"""
    cart_service = CartService()
    try:
        cart_service.remove_item(product_id)
        flash('محصول از سبد خرید حذف شد', 'success')
    except Exception as e:
        flash('خطا در حذف محصول', 'error')
    return redirect(url_for('main.cart'))


@main_bp.route('/cart/clear', methods=['POST'])
def cart_clear():
    """Clear all items from cart"""
    cart_service = CartService()
    cart_service.clear_cart()
    flash('سبد خرید خالی شد', 'success')
    return redirect(url_for('main.cart'))


# User Authentication Routes
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        phone = ''.join(filter(str.isdigit, form.phone.data))
        
        # Check if user already exists
        existing_user = get_user_by_username(phone)
        if existing_user:
            flash('این شماره تلفن قبلا ثبت شده است. لطفا وارد شوید.', 'error')
            return redirect(url_for('main.login'))
        
        # Create user
        with next(get_session()) as db:
            try:
                user_service = UserService(db)
                new_user = user_service.create_user_from_phone(
                    phone=phone,
                    email=form.email.data or None,
                    name=form.name.data
                )
                
                # Set custom password if provided
                if form.password.data:
                    if form.password.data != form.password_confirm.data:
                        flash('رمز عبور و تکرار آن مطابقت ندارند', 'error')
                        return render_template('register.html', form=form)
                    new_user.set_password(form.password.data)
                
                db.commit()
                
                # Auto-login after registration
                login_user(new_user, remember=True)
                flash('ثبت نام با موفقیت انجام شد', 'success')
                return redirect(url_for('main.index'))
            except Exception as e:
                db.rollback()
                flash('خطا در ثبت نام. لطفا دوباره تلاش کنید.', 'error')
    
    return render_template('register.html', form=form)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        phone = ''.join(filter(str.isdigit, form.phone.data))
        user = get_user_by_username(phone)
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('حساب کاربری شما غیرفعال است', 'error')
                return render_template('user_login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('main.index')
            flash('ورود موفقیت‌آمیز بود', 'success')
            return redirect(next_page)
        else:
            flash('شماره تلفن یا رمز عبور اشتباه است', 'error')
    
    return render_template('user_login.html', form=form)


@main_bp.route('/logout')
def logout():
    """User logout - clears flask-login and OAuth session info"""
    try:
        logout_user()
    except Exception:
        pass
    session.pop('oauth_user', None)
    flash('خروج موفقیت‌آمیز بود', 'success')
    return redirect(url_for('main.index'))


@main_bp.route('/login/google')
def login_google():
    """Start Google OAuth login"""
    # Use HTTPS external URL for redirect
    redirect_uri = url_for('main.auth_google_callback', _external=True, _scheme='https')
    try:
        return current_app.oauth.google.authorize_redirect(redirect_uri)
    except Exception:
        flash('Google OAuth پیکربندی نشده است. لطفا متغیرهای محیطی را بررسی کنید.', 'error')
        return redirect(url_for('main.login'))


@main_bp.route('/authorize')
def authorize():
    """Legacy OAuth callback route — delegate to unified handler to avoid duplicated logic"""
    return auth_google_callback()


@main_bp.route('/auth/google/callback')
def auth_google_callback():
    """OAuth2 callback handler for Google - unified handler that upserts user and logs them in"""
    try:
        # Exchange code for token
        token = current_app.oauth.google.authorize_access_token()
        if not token:
            flash('خطا در احراز هویت گوگل', 'error')
            return redirect(url_for('main.login'))

        # Fetch user info (OpenID Connect userinfo endpoint)
        resp = current_app.oauth.google.get('userinfo')
        user_info = {}
        try:
            user_info = resp.json() if resp else {}
        except Exception:
            user_info = {}

        if not user_info or not user_info.get('email'):
            flash('خطا در دریافت اطلاعات کاربری از گوگل', 'error')
            return redirect(url_for('main.login'))

        email = user_info.get('email')
        name = user_info.get('name') or email.split('@')[0]

        # Upsert user and login
        with next(get_session()) as db:
            user_service = UserService(db)
            user = user_service.get_user_by_email(email)

            try:
                if not user:
                    # Create new user for OAuth login (no phone)
                    user = user_service.create_user_from_phone(
                        phone=None,
                        email=email,
                        name=name
                    )
                    db.commit()
                else:
                    # Optional: update user's name/avatar if desired (safe best-effort)
                    try:
                        updated = False
                        if getattr(user, 'Name', None) and user.Name != name:
                            user.Name = name
                            updated = True
                        if getattr(user, 'name', None) and user.name != name:
                            user.name = name
                            updated = True
                        # If your User model has avatar/picture fields, update similarly:
                        picture = user_info.get('picture')
                        if picture:
                            if hasattr(user, 'Avatar') and user.Avatar != picture:
                                user.Avatar = picture
                                updated = True
                            if hasattr(user, 'avatar') and user.avatar != picture:
                                user.avatar = picture
                                updated = True
                        if updated:
                            db.commit()
                    except Exception:
                        # non-fatal: continue without failing login
                        db.rollback()

                # Ensure user is active if your model supports it
                is_active = True
                if hasattr(user, 'is_active'):
                    is_active = getattr(user, 'is_active')
                if hasattr(user, 'IsActive'):
                    is_active = getattr(user, 'IsActive')

                if not is_active:
                    flash('حساب کاربری شما غیرفعال است', 'error')
                    return redirect(url_for('main.login'))

                # Login user with flask-login
                login_user(user, remember=True)

                # Store OAuth info in session for UI
                session['oauth_user'] = {
                    'name': user_info.get('name') or name,
                    'email': email,
                    'picture': user_info.get('picture')
                }

            except Exception as e:
                db.rollback()
                current_app.logger.exception('Error upserting Google user: %s', e)
                flash('خطا در پردازش حساب کاربری. لطفا دوباره تلاش کنید.', 'error')
                return redirect(url_for('main.login'))

        # Redirect to stored destination or index
        dest = session.pop('redirect_after_login', None) or url_for('main.index')
        flash('ورود با گوگل با موفقیت انجام شد', 'success')
        return redirect(dest)

    except Exception as e:
        current_app.logger.exception('Google OAuth callback failed: %s', e)
        flash(f'خطا در ورود با گوگل: {str(e)}', 'error')
        return redirect(url_for('main.login'))




# Checkout Routes
@main_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page with phone verification"""
    cart_service = CartService()
    
    # Validate cart
    is_valid, error_msg = cart_service.validate_cart()
    if not is_valid:
        flash(error_msg or 'سبد خرید خالی است', 'error')
        return redirect(url_for('main.cart'))
    
    cart_items = cart_service.get_cart_with_products()
    cart_total = cart_service.get_cart_total()
    
    # Step 1: Phone verification (if not verified)
    verification_service = PhoneVerificationService()
    verified_phone = session.get('verified_phone')
    
    if not verified_phone:
        form = PhoneVerificationForm()
        if form.validate_on_submit():
            phone = ''.join(filter(str.isdigit, form.phone.data))
            
            # Check if OTP is being submitted
            if form.otp.data:
                # Verify OTP
                success, message = verification_service.verify_otp(phone, form.otp.data)
                if success:
                    session['verified_phone'] = phone
                    flash(message, 'success')
                    return redirect(url_for('main.checkout'))
                else:
                    flash(message, 'error')
            else:
                # Send OTP
                result = verification_service.send_otp(phone)
                if result.get('success'):
                    flash(result.get('message'), 'success')
                    # In development, show OTP
                    if 'otp' in result:
                        flash(f'کد تایید (برای تست): {result["otp"]}', 'info')
                else:
                    flash('خطا در ارسال کد تایید', 'error')
        
        return render_template('checkout_verification.html',
                             form=form,
                             cart_items=cart_items,
                             cart_total=cart_total)
    
    # Step 2: Checkout form (after phone verification)
    checkout_form = CheckoutForm()
    if checkout_form.validate_on_submit():
        # Create order
        with next(get_session()) as db:
            order_service = OrderService(db)
            user_service = UserService(db)
            
            try:
                # Auto-create user account if doesn't exist
                user = user_service.get_user_by_phone(verified_phone)
                user_id = user.id if user else None
                
                if not user:
                    # Create user account automatically
                    user = user_service.create_user_from_phone(
                        phone=verified_phone,
                        email=checkout_form.email.data or None,
                        name=checkout_form.name.data
                    )
                    db.commit()
                    user_id = user.id
                    
                    # Auto-login the newly created user
                    login_user(user, remember=False)
                
                # Create order
                cart = cart_service.get_cart()
                order = order_service.create_order_from_cart(
                    cart_items=cart,
                    customer_name=checkout_form.name.data,
                    customer_phone=verified_phone,
                    customer_email=checkout_form.email.data or None,
                    shipping_address=checkout_form.shipping_address.data or None,
                    user_id=user_id,
                    notes=checkout_form.notes.data or None
                )
                
                db.commit()
                
                # Store order ID in session for payment
                session['pending_order_id'] = order.Id
                session['pending_order_number'] = order.OrderNumber
                
                # Clear verification and cart
                verification_service.clear_verification()
                session.pop('verified_phone', None)
                
                # Redirect to payment
                return redirect(url_for('main.payment', order_id=order.Id))
                
            except Exception as e:
                db.rollback()
                flash(f'خطا در ایجاد سفارش: {str(e)}', 'error')
    
    return render_template('checkout.html',
                         form=checkout_form,
                         cart_items=cart_items,
                         cart_total=cart_total,
                         verified_phone=verified_phone)


@main_bp.route('/checkout/send-otp', methods=['POST'])
def send_otp():
    """API endpoint to send OTP"""
    verification_service = PhoneVerificationService()
    data = request.get_json() or {}
    phone = data.get('phone', '')
    
    if not phone:
        return jsonify({'success': False, 'message': 'شماره تلفن الزامی است'}), 400
    
    result = verification_service.send_otp(phone)
    return jsonify(result)


@main_bp.route('/payment/<order_id>', methods=['GET', 'POST'])
def payment(order_id):
    """Payment page"""
    with next(get_session()) as db:
        order_service = OrderService(db)
        order = order_service.get_order(order_id)
        
        if not order:
            flash('سفارش یافت نشد', 'error')
            return redirect(url_for('main.index'))
        
        # In a real implementation, integrate with payment gateway
        # For now, show order summary and mock payment button
        return render_template('payment.html', order=order)


@main_bp.route('/order/success/<order_number>')
def order_success(order_number):
    """Order success page"""
    with next(get_session()) as db:
        order_service = OrderService(db)
        order = order_service.get_order_by_number(order_number)
        
        if not order:
            flash('سفارش یافت نشد', 'error')
            return redirect(url_for('main.index'))
        
        return render_template('order_success.html', order=order)

@main_bp.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = Path(get_upload_folder())
    # Ensure the file exists
    file_path = upload_folder / filename
    if file_path.exists():
        return send_from_directory(str(upload_folder), filename)
    return "File not found", 404
