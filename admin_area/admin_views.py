"""
Admin Area Admin Views
Custom views for Flask-Admin
"""
from flask import redirect, url_for, flash
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from datetime import datetime, date
from app.utils.upload import save_uploaded_file, delete_uploaded_file
from app.utils.persian_date import to_persian_date
from admin_area.form_fields import ImageUploadField, CKEditorField


class AdminIndexView(AdminIndexView):
    """Custom admin index view with authentication check and statistics"""
    
    # Use custom RTL base template
    base_template = 'admin_base.html'
    template = 'admin/index.html'

    def is_accessible(self):
        """Check if user can access admin panel"""
        return current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login if not accessible"""
        flash('برای دسترسی به این بخش، باید به عنوان مدیر وارد شوید.', 'warning')
        return redirect(url_for('admin_area.login', next='/admin'))
    
    @expose('/')
    def index(self):
        """Render admin dashboard with statistics"""
        from app.models.models import Products, Categories, Blogs, BlogCategories, ProductComments, ProductImages
        from app.repositories.db import get_scoped_session
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        Session = get_scoped_session()
        db = Session()
        
        try:
            # Basic statistics
            total_products = db.query(Products).filter(Products.IsDeleted == False).count()
            active_products = db.query(Products).filter(
                and_(Products.IsDeleted == False, Products.IsActive == True)
            ).count()
            total_categories = db.query(Categories).filter(Categories.IsDeleted == False).count()
            total_blogs = db.query(Blogs).filter(Blogs.IsDeleted == False).count()
            published_blogs = db.query(Blogs).filter(
                and_(Blogs.IsDeleted == False, Blogs.IsPublished == True)
            ).count()
            total_comments = db.query(ProductComments).filter(ProductComments.IsDeleted == False).count()
            pending_comments = db.query(ProductComments).filter(
                and_(ProductComments.IsDeleted == False, ProductComments.IsApproved == False)
            ).count()
            
            # Products without images
            products_without_images = db.query(Products).filter(
                and_(
                    Products.IsDeleted == False,
                    (Products.MainImageUrl == None) | (Products.MainImageUrl == '')
                )
            ).count()
            
            # Low stock products (stock < 10)
            low_stock_products = db.query(Products).filter(
                and_(
                    Products.IsDeleted == False,
                    Products.IsActive == True,
                    Products.Stock < 10
                )
            ).count()
            
            # Products by category (for pie chart)
            category_stats = db.query(
                Categories.Title,
                func.count(Products.Id).label('count')
            ).join(
                Products, Categories.Id == Products.CategoryId, isouter=True
            ).filter(
                and_(Categories.IsDeleted == False, Products.IsDeleted == False)
            ).group_by(Categories.Id, Categories.Title).all()
            
            category_labels = [cat[0] or 'بدون دسته‌بندی' for cat in category_stats]
            category_counts = [cat[1] for cat in category_stats]
            
            # Recent products (last 10)
            recent_products = db.query(Products).filter(
                Products.IsDeleted == False
            ).order_by(Products.CreatedAt.desc()).limit(10).all()
            
            # Recent comments (last 10)
            recent_comments = db.query(ProductComments).filter(
                ProductComments.IsDeleted == False
            ).order_by(ProductComments.CreatedAt.desc()).limit(10).all()
            
            # Products created in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_products_count = db.query(Products).filter(
                and_(
                    Products.IsDeleted == False,
                    Products.CreatedAt >= thirty_days_ago
                )
            ).count()
            
            # Featured products count
            featured_products = db.query(Products).filter(
                and_(
                    Products.IsDeleted == False,
                    Products.IsActive == True,
                    Products.IsFeatured == True
                )
            ).count()
            
            stats = {
                'total_products': total_products,
                'active_products': active_products,
                'total_categories': total_categories,
                'total_blogs': total_blogs,
                'published_blogs': published_blogs,
                'total_comments': total_comments,
                'pending_comments': pending_comments,
                'products_without_images': products_without_images,
                'low_stock_products': low_stock_products,
                'featured_products': featured_products,
                'recent_products_count': recent_products_count,
                'category_labels': category_labels,
                'category_counts': category_counts,
                'recent_products': recent_products,
                'recent_comments': recent_comments,
            }
            
            return self.render('admin/index.html', stats=stats)
        finally:
            db.close()


class SecureModelView(ModelView):
    """Base ModelView that is only accessible to admin users."""
    
    # Use custom RTL base template
    base_template = 'admin_base.html'

    def __init__(self, model, session, **kwargs):
        super(SecureModelView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        """Check if user can access this view"""
        return current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login if not accessible"""
        flash('برای دسترسی به این بخش، باید به عنوان مدیر وارد شوید.', 'warning')
        return redirect(url_for('admin_area.login', next='/admin'))


class LocalizedModelView(SecureModelView):
    """
    ModelView that reads Persian labels from SQLAlchemy Column.info['label_fa']
    so you don't have to hard-code field names in every view.
    Also formats dates to Persian (Shamsi) format.
    Automatically handles audit fields (CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted).
    """

    def __init__(self, model, session, **kwargs):
        # Build column_labels from model column info before calling parent init
        labels = {}
        date_formatters = {}
        table = getattr(model, "__table__", None)
        if table is not None:
            for col in table.columns:
                label_fa = getattr(col, "info", {}).get("label_fa")
                if label_fa:
                    labels[col.name] = label_fa
                
                # Check if column is a date/datetime type
                if hasattr(col.type, 'python_type'):
                    col_type = col.type.python_type
                    if col_type in (datetime, date):
                        date_formatters[col.name] = self._persian_date_formatter

        if labels:
            existing = getattr(self, "column_labels", {}) or {}
            # merge, but don't overwrite explicit labels set on the class
            merged = {**labels, **existing}
            self.column_labels = merged

        # Set date formatters
        if date_formatters:
            existing_formatters = getattr(self, "column_formatters", {}) or {}
            existing_formatters.update(date_formatters)
            self.column_formatters = existing_formatters

        # Ensure audit fields are excluded
        audit_fields = ['IsDeleted', 'CreatedAt', 'CreatedBy', 'UpdatedAt', 'UpdatedBy', 'DeletedAt', 'DeletedBy']
        existing_excluded = getattr(self, "form_excluded_columns", None) or ()
        combined_excluded = set(existing_excluded) | set(audit_fields)
        self.form_excluded_columns = tuple(combined_excluded)

        super().__init__(model, session, **kwargs)
    
    def _persian_date_formatter(self, view, context, model, name):
        """Format date/datetime fields to Persian date"""
        value = getattr(model, name, None)
        if value is None:
            return ''
        try:
            return to_persian_date(value)
        except Exception:
            # Fallback to original value if conversion fails
            return str(value) if value else ''
    
    def on_model_create(self, model):
        """Automatically set CreatedAt and CreatedBy on create"""
        if hasattr(model, 'CreatedAt') and not model.CreatedAt:
            model.CreatedAt = datetime.utcnow()
        if hasattr(model, 'CreatedBy') and current_user.is_authenticated:
            model.CreatedBy = str(current_user.id) if hasattr(current_user, 'id') else None
        if hasattr(model, 'IsDeleted'):
            model.IsDeleted = False
        if hasattr(model, 'AuthorId') and not model.AuthorId and current_user.is_authenticated:
            model.AuthorId = str(current_user.id) if hasattr(current_user, 'id') else None
        super(LocalizedModelView, self).on_model_create(model)
    
    def on_model_change(self, form, model, is_created):
        """Automatically set UpdatedAt and UpdatedBy on update"""
        if not is_created:
            if hasattr(model, 'UpdatedAt'):
                model.UpdatedAt = datetime.utcnow()
            if hasattr(model, 'UpdatedBy') and current_user.is_authenticated:
                model.UpdatedBy = str(current_user.id) if hasattr(current_user, 'id') else None
        super(LocalizedModelView, self).on_model_change(form, model, is_created)


class PostModelView(LocalizedModelView):
    """Custom ModelView for Post model"""

    # Configure columns
    column_list = ('id', 'title', 'slug', 'is_published', 'created_at')
    column_searchable_list = ('title', 'slug', 'content')
    column_filters = ('is_published', 'created_at')
    column_editable_list = ('is_published',)
    form_columns = ('title', 'slug', 'content', 'excerpt', 'is_published')
    
    form_excluded_columns = (
        'id',
        'created_at',
        'updated_at',
    )

    # Page size
    page_size = 20


class CategoryAdminView(LocalizedModelView):
    """Admin view for product groups / categories."""

    column_list = ('Id', 'Title', 'Slug', 'IsActive', 'SortOrder')
    column_filters = ('IsActive',)

    # Only show business fields in the form; system fields are filled automatically
    form_columns = (
        'ParentId',
        'Title',
        'TitleEn',
        'TitleAr',
        'Slug',
        'SlugEn',
        'SlugAr',
        'Description',
        'DescriptionEn',
        'DescriptionAr',
        'SortOrder',
        'IsActive',
    )

    form_excluded_columns = (
        'IsDeleted',
        'CreatedAt',
        'CreatedBy',
        'UpdatedAt',
        'UpdatedBy',
        'DeletedAt',
        'DeletedBy',
        'children',
        'products',
    )


class BlogCategoryAdminView(LocalizedModelView):
    """Admin view for blog categories."""

    column_list = ('Id', 'Title', 'Slug', 'IsActive')
    column_filters = ('IsActive',)
    column_searchable_list = ('Title', 'Slug')

    form_columns = (
        'Title',
        'TitleEn',
        'TitleAr',
        'Slug',
        'SlugEn',
        'SlugAr',
        'Description',
        'IsActive',
    )

    form_excluded_columns = (
        'Id',
        'IsDeleted',
        'CreatedAt',
        'CreatedBy',
        'UpdatedAt',
        'UpdatedBy',
        'DeletedAt',
        'DeletedBy',
        'blogs',
    )


class ProductAdminView(LocalizedModelView):
    """Admin view for products."""

    # Show readable category and main business fields
    column_list = (
        'Id',
        'Title',
        'Slug',
        'category',
        'Price',
        'Stock',
        'IsActive',
        'IsFeatured',
    )

    column_filters = ('IsActive', 'IsFeatured')
    column_searchable_list = ('Title', 'Slug', 'SKU')

    # Use relationship 'category' so dropdown shows category titles instead of raw FK
    form_columns = (
        'category',
        'SKU',
        'Title',
        'TitleEn',
        'TitleAr',
        'Slug',
        'SlugEn',
        'SlugAr',
        'ShortDescription',
        'ShortDescriptionEn',
        'ShortDescriptionAr',
        'Description',
        'DescriptionEn',
        'DescriptionAr',
        'Price',
        'Stock',
        'IsActive',
        'IsFeatured',
        'MetaTitle',
        'MetaDescription',
        'MetaKeywords',
    )

    # Hide system/audit columns from the form
    form_excluded_columns = (
        'Id',
        'CategoryId',
        'IsDeleted',
        'CreatedAt',
        'CreatedBy',
        'UpdatedAt',
        'UpdatedBy',
        'DeletedAt',
        'DeletedBy',
        'images',
        'comments',
        'MainImageUrl',
    )
    
    def scaffold_form(self):
        """Create form with custom image upload field"""
        form_class = super(ProductAdminView, self).scaffold_form()
        
        # Remove MainImageUrl field if it exists
        if hasattr(form_class, 'MainImageUrl'):
            delattr(form_class, 'MainImageUrl')
        
        # Add image upload field
        form_class.MainImageFile = ImageUploadField(
            label='تصویر اصلی',
            image_url_field='MainImageUrl'
        )
        
        return form_class
    
    def on_form_prefill(self, form, id):
        """Set current image URL for preview on edit"""
        obj = self.get_one(id)
        if obj and hasattr(obj, 'MainImageUrl') and obj.MainImageUrl:
            form.MainImageFile.current_url = obj.MainImageUrl
    
    def on_model_change(self, form, model, is_created):
        """Handle file upload when saving"""
        # Handle image upload
        if hasattr(form, 'MainImageFile') and form.MainImageFile.data:
            uploaded_file = form.MainImageFile.data
            if uploaded_file and uploaded_file.filename:
                try:
                    # Delete old image if exists
                    if not is_created and model.MainImageUrl:
                        delete_uploaded_file(model.MainImageUrl)
                    
                    # Save new image
                    image_url = save_uploaded_file(uploaded_file, subfolder='products')
                    if image_url:
                        model.MainImageUrl = image_url
                except Exception as e:
                    flash(f'خطا در آپلود تصویر: {str(e)}', 'error')
        
        super(ProductAdminView, self).on_model_change(form, model, is_created)
    
    def on_model_create(self, model):
        """Ensure audit fields are handled"""
        super(ProductAdminView, self).on_model_create(model)
    
    def on_model_delete(self, model):
        """Delete associated image file when model is deleted"""
        if model.MainImageUrl:
            delete_uploaded_file(model.MainImageUrl)
        super(ProductAdminView, self).on_model_delete(model)


class SiteContentAdminView(LocalizedModelView):
    """Admin view for site content sections."""
    
    column_list = (
        'SectionKey',
        'SectionName',
        'Title',
        'IsActive',
        'SortOrder',
    )
    
    column_filters = ('IsActive', 'SectionKey')
    column_searchable_list = ('SectionKey', 'SectionName', 'Title', 'Content')
    
    form_columns = (
        'SectionKey',
        'SectionName',
        'Title',
        'Subtitle',
        'Content',
        'ContentEn',
        'ContentAr',
        'VideoUrl',
        'LinkUrl',
        'LinkText',
        'Field1',
        'Field2',
        'Field3',
        'Field4',
        'JsonData',
        'SortOrder',
        'IsActive',
    )
    
    form_excluded_columns = (
        'Id',
        'IsDeleted',
        'CreatedAt',
        'CreatedBy',
        'UpdatedAt',
        'UpdatedBy',
        'DeletedAt',
        'DeletedBy',
        'ImageUrl',
    )
    
    # Page size
    page_size = 50
    
    def scaffold_form(self):
        """Create form with custom image upload field"""
        form_class = super(SiteContentAdminView, self).scaffold_form()
        
        # Remove ImageUrl field if it exists
        if hasattr(form_class, 'ImageUrl'):
            delattr(form_class, 'ImageUrl')
        
        # Add image upload field
        form_class.ImageFile = ImageUploadField(
            label='تصویر',
            image_url_field='ImageUrl'
        )
        
        return form_class
    
    def on_form_prefill(self, form, id):
        """Set current image URL for preview on edit"""
        obj = self.get_one(id)
        if obj and hasattr(obj, 'ImageUrl') and obj.ImageUrl:
            form.ImageFile.current_url = obj.ImageUrl
    
    def on_model_change(self, form, model, is_created):
        """Handle file upload when saving"""
        # Handle image upload
        if hasattr(form, 'ImageFile') and form.ImageFile.data:
            uploaded_file = form.ImageFile.data
            if uploaded_file and uploaded_file.filename:
                try:
                    # Delete old image if exists
                    if not is_created and model.ImageUrl:
                        delete_uploaded_file(model.ImageUrl)
                    
                    # Save new image
                    image_url = save_uploaded_file(uploaded_file, subfolder='site-content')
                    if image_url:
                        model.ImageUrl = image_url
                except Exception as e:
                    flash(f'خطا در آپلود تصویر: {str(e)}', 'error')
        
        super(SiteContentAdminView, self).on_model_change(form, model, is_created)
    
    def on_model_create(self, model):
        """Ensure audit fields are handled"""
        super(SiteContentAdminView, self).on_model_create(model)
    
    def on_model_delete(self, model):
        """Delete associated image file when model is deleted"""
        if model.ImageUrl:
            delete_uploaded_file(model.ImageUrl)
        super(SiteContentAdminView, self).on_model_delete(model)


class BlogAdminView(LocalizedModelView):
    """Admin view for blog posts with image upload support."""
    
    column_list = (
        'Id',
        'Title',
        'Slug',
        'category',
        'IsPublished',
        'Views',
    )
    
    column_filters = ('IsPublished', 'category')
    column_searchable_list = ('Title', 'Slug', 'Excerpt')
    
    form_columns = (
        'category',
        'Title',
        'TitleEn',
        'TitleAr',
        'Slug',
        'SlugEn',
        'SlugAr',
        'Excerpt',
        'ExcerptEn',
        'ExcerptAr',
        'Body',
        'BodyEn',
        'BodyAr',
        'IsPublished',
        'PublishedAt',
    )
    
    form_excluded_columns = (
        'Id',
        'BlogCategoryId',
        'AuthorId',
        'IsDeleted',
        'CreatedAt',
        'CreatedBy',
        'UpdatedAt',
        'UpdatedBy',
        'DeletedAt',
        'DeletedBy',
        'Views',
        'FeaturedImageUrl',
        'comments',
    )
    
    def scaffold_form(self):
        """Create form with custom image upload field and CKEditor"""
        form_class = super(BlogAdminView, self).scaffold_form()
        
        # Remove FeaturedImageUrl field if it exists
        if hasattr(form_class, 'FeaturedImageUrl'):
            delattr(form_class, 'FeaturedImageUrl')
        
        # Add image upload field
        form_class.FeaturedImageFile = ImageUploadField(
            label='تصویر شاخص',
            image_url_field='FeaturedImageUrl'
        )
        
        # Replace Body fields with CKEditor
        if hasattr(form_class, 'Body'):
            form_class.Body = CKEditorField(label='محتوا')
        if hasattr(form_class, 'BodyEn'):
            form_class.BodyEn = CKEditorField(label='محتوا (انگلیسی)')
        if hasattr(form_class, 'BodyAr'):
            form_class.BodyAr = CKEditorField(label='محتوا (عربی)')
        
        return form_class
    
    def on_form_prefill(self, form, id):
        """Set current image URL for preview on edit"""
        obj = self.get_one(id)
        if obj and hasattr(obj, 'FeaturedImageUrl') and obj.FeaturedImageUrl:
            form.FeaturedImageFile.current_url = obj.FeaturedImageUrl
    
    def on_model_change(self, form, model, is_created):
        """Handle file upload when saving"""
        # Handle image upload
        if hasattr(form, 'FeaturedImageFile') and form.FeaturedImageFile.data:
            uploaded_file = form.FeaturedImageFile.data
            if uploaded_file and uploaded_file.filename:
                try:
                    # Delete old image if exists
                    if not is_created and model.FeaturedImageUrl:
                        delete_uploaded_file(model.FeaturedImageUrl)
                    
                    # Save new image
                    image_url = save_uploaded_file(uploaded_file, subfolder='blogs')
                    if image_url:
                        model.FeaturedImageUrl = image_url
                except Exception as e:
                    flash(f'خطا در آپلود تصویر: {str(e)}', 'error')
        
        super(BlogAdminView, self).on_model_change(form, model, is_created)
    
    def on_model_create(self, model):
        """Ensure audit fields are handled"""
        super(BlogAdminView, self).on_model_create(model)
    
    def on_model_delete(self, model):
        """Delete associated image file when model is deleted"""
        if model.FeaturedImageUrl:
            delete_uploaded_file(model.FeaturedImageUrl)
        super(BlogAdminView, self).on_model_delete(model)

