"""
Lightweight models for the shop and blog based on the 8-table schema.

Notes:
- Use GUID primary keys stored as string UUID (36 chars) for cross-DB compatibility.
- Soft delete and audit fields are present on all tables.
"""
from datetime import datetime
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def new_guid_str() -> str:
    return str(uuid.uuid4())


class Categories(Base):
    __tablename__ = 'Categories'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    ParentId = Column(String(36), ForeignKey('Categories.Id'), nullable=True, info={"label_fa": "دسته والد"})

    Title = Column(String(255), nullable=False, info={"label_fa": "عنوان"})
    TitleEn = Column(String(255), nullable=True, info={"label_fa": "عنوان (انگلیسی)"})
    TitleAr = Column(String(255), nullable=True, info={"label_fa": "عنوان (عربی)"})

    Slug = Column(String(255), nullable=False, info={"label_fa": "نامک"})
    SlugEn = Column(String(255), nullable=True, info={"label_fa": "نامک (انگلیسی)"})
    SlugAr = Column(String(255), nullable=True, info={"label_fa": "نامک (عربی)"})

    Description = Column(Text, nullable=True, info={"label_fa": "توضیحات"})
    DescriptionEn = Column(Text, nullable=True, info={"label_fa": "توضیحات (انگلیسی)"})
    DescriptionAr = Column(Text, nullable=True, info={"label_fa": "توضیحات (عربی)"})

    SortOrder = Column(Integer, nullable=False, default=0, info={"label_fa": "ترتیب نمایش"})
    IsActive = Column(Boolean, nullable=False, default=True, info={"label_fa": "فعال"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    parent = relationship('Categories', remote_side=[Id], backref='children', foreign_keys=[ParentId])

    def __str__(self):
        # Used by Flask-Admin to show readable category names
        return self.Title or str(self.Id)


class Products(Base):
    __tablename__ = 'Products'
    Id = Column(String(36), primary_key=True, default=new_guid_str)
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    CategoryId = Column(String(36), ForeignKey('Categories.Id'), nullable=True, info={"label_fa": "دسته"})
    SKU = Column(String(100), nullable=True, unique=True, info={"label_fa": "کد محصول (SKU)"})

    Title = Column(String(255), nullable=False, info={"label_fa": "عنوان"})
    TitleEn = Column(String(255), nullable=True, info={"label_fa": "عنوان (انگلیسی)"})
    TitleAr = Column(String(255), nullable=True, info={"label_fa": "عنوان (عربی)"})

    Slug = Column(String(255), nullable=False, info={"label_fa": "نامک"})
    SlugEn = Column(String(255), nullable=True, info={"label_fa": "نامک (انگلیسی)"})
    SlugAr = Column(String(255), nullable=True, info={"label_fa": "نامک (عربی)"})

    ShortDescription = Column(String(1000), nullable=True, info={"label_fa": "توضیح کوتاه"})
    ShortDescriptionEn = Column(String(1000), nullable=True, info={"label_fa": "توضیح کوتاه (انگلیسی)"})
    ShortDescriptionAr = Column(String(1000), nullable=True, info={"label_fa": "توضیح کوتاه (عربی)"})

    Description = Column(Text, nullable=True, info={"label_fa": "توضیحات"})
    DescriptionEn = Column(Text, nullable=True, info={"label_fa": "توضیحات (انگلیسی)"})
    DescriptionAr = Column(Text, nullable=True, info={"label_fa": "توضیحات (عربی)"})

    Price = Column(Numeric(18, 2), nullable=False, info={"label_fa": "قیمت"})
    Stock = Column(Numeric(18, 2), nullable=False, default=0, info={"label_fa": "موجودی"})

    IsActive = Column(Boolean, nullable=False, default=True, info={"label_fa": "فعال"})
    IsFeatured = Column(Boolean, nullable=False, default=False, info={"label_fa": "ویژه"})

    MainImageUrl = Column(String(500), nullable=True, info={"label_fa": "تصویر اصلی"})
    MetaTitle = Column(String(255), nullable=True, info={"label_fa": "عنوان متا"})
    MetaDescription = Column(String(500), nullable=True, info={"label_fa": "توضیحات متا"})
    MetaKeywords = Column(String(500), nullable=True, info={"label_fa": "کلمات کلیدی متا"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    category = relationship('Categories', backref='products')

    def __str__(self):
        return self.Title or str(self.Id)

    def __str__(self):
        # Used by Flask-Admin to show a readable label in dropdowns
        return self.Title or str(self.Id)


class ProductImages(Base):
    __tablename__ = 'ProductImages'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    ProductId = Column(String(36), ForeignKey('Products.Id'), nullable=False, info={"label_fa": "محصول"})

    ImageUrl = Column(String(500), nullable=False, info={"label_fa": "آدرس تصویر"})
    AltText = Column(String(255), nullable=True, info={"label_fa": "متن جایگزین"})
    AltTextEn = Column(String(255), nullable=True, info={"label_fa": "متن جایگزین (انگلیسی)"})
    AltTextAr = Column(String(255), nullable=True, info={"label_fa": "متن جایگزین (عربی)"})

    IsPrimary = Column(Boolean, nullable=False, default=False, info={"label_fa": "تصویر اصلی"})
    SortOrder = Column(Integer, nullable=False, default=0, info={"label_fa": "ترتیب نمایش"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    product = relationship('Products', backref='images')


class ProductDocuments(Base):
    __tablename__ = 'ProductDocuments'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    ProductId = Column(String(36), ForeignKey('Products.Id'), nullable=False, info={"label_fa": "محصول"})

    FileUrl = Column(String(1000), nullable=False, info={"label_fa": "آدرس فایل"})
    FileName = Column(String(500), nullable=True, info={"label_fa": "نام فایل"})
    ContentType = Column(String(255), nullable=True, info={"label_fa": "نوع محتوا"})
    FileSize = Column(Integer, nullable=True, info={"label_fa": "حجم (بایت)"})
    SortOrder = Column(Integer, nullable=False, default=0, info={"label_fa": "ترتیب نمایش"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    product = relationship('Products', backref='documents')


class BlogCategories(Base):
    __tablename__ = 'BlogCategories'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})

    Title = Column(String(255), nullable=False, info={"label_fa": "عنوان"})
    TitleEn = Column(String(255), nullable=True, info={"label_fa": "عنوان (انگلیسی)"})
    TitleAr = Column(String(255), nullable=True, info={"label_fa": "عنوان (عربی)"})

    Slug = Column(String(255), nullable=False, info={"label_fa": "نامک"})
    SlugEn = Column(String(255), nullable=True, info={"label_fa": "نامک (انگلیسی)"})
    SlugAr = Column(String(255), nullable=True, info={"label_fa": "نامک (عربی)"})

    Description = Column(Text, nullable=True, info={"label_fa": "توضیحات"})
    IsActive = Column(Boolean, nullable=False, default=True, info={"label_fa": "فعال"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    def __str__(self):
        return self.Title or str(self.Id)


class Blogs(Base):
    __tablename__ = 'Blogs'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    BlogCategoryId = Column(String(36), ForeignKey('BlogCategories.Id'), nullable=True, info={"label_fa": "دسته‌بندی"})
    AuthorId = Column(String(36), nullable=True, info={"label_fa": "نویسنده"})

    Title = Column(String(255), nullable=False, info={"label_fa": "عنوان"})
    TitleEn = Column(String(255), nullable=True, info={"label_fa": "عنوان (انگلیسی)"})
    TitleAr = Column(String(255), nullable=True, info={"label_fa": "عنوان (عربی)"})

    Slug = Column(String(255), nullable=False, info={"label_fa": "نامک"})
    SlugEn = Column(String(255), nullable=True, info={"label_fa": "نامک (انگلیسی)"})
    SlugAr = Column(String(255), nullable=True, info={"label_fa": "نامک (عربی)"})

    Excerpt = Column(String(1000), nullable=True, info={"label_fa": "خلاصه"})
    ExcerptEn = Column(String(1000), nullable=True, info={"label_fa": "خلاصه (انگلیسی)"})
    ExcerptAr = Column(String(1000), nullable=True, info={"label_fa": "خلاصه (عربی)"})

    Body = Column(Text, nullable=True, info={"label_fa": "متن"})
    BodyEn = Column(Text, nullable=True, info={"label_fa": "متن (انگلیسی)"})
    BodyAr = Column(Text, nullable=True, info={"label_fa": "متن (عربی)"})

    FeaturedImageUrl = Column(String(500), nullable=True, info={"label_fa": "تصویر شاخص"})
    IsPublished = Column(Boolean, nullable=False, default=False, info={"label_fa": "منتشر شده"})
    PublishedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ انتشار"})
    Views = Column(Integer, nullable=False, default=0, info={"label_fa": "بازدید"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    category = relationship('BlogCategories', backref='blogs')


class BlogComments(Base):
    __tablename__ = 'BlogComments'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    BlogId = Column(String(36), ForeignKey('Blogs.Id'), nullable=False, info={"label_fa": "مقاله"})
    ParentId = Column(String(36), ForeignKey('BlogComments.Id'), nullable=True, info={"label_fa": "والد"})
    UserId = Column(String(36), nullable=True, info={"label_fa": "کاربر"})

    Body = Column(Text, nullable=False, info={"label_fa": "متن"})
    BodyEn = Column(Text, nullable=True, info={"label_fa": "متن (انگلیسی)"})
    BodyAr = Column(Text, nullable=True, info={"label_fa": "متن (عربی)"})
    IsApproved = Column(Boolean, nullable=False, default=False, info={"label_fa": "تایید شده"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    blog = relationship('Blogs', backref='comments')
    parent = relationship('BlogComments', remote_side=[Id], backref='replies')


class ProductComments(Base):
    __tablename__ = 'ProductComments'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    ProductId = Column(String(36), ForeignKey('Products.Id'), nullable=False, info={"label_fa": "محصول"})
    ParentId = Column(String(36), ForeignKey('ProductComments.Id'), nullable=True, info={"label_fa": "والد"})
    UserId = Column(String(36), nullable=True, info={"label_fa": "کاربر"})

    Body = Column(Text, nullable=False, info={"label_fa": "متن"})
    BodyEn = Column(Text, nullable=True, info={"label_fa": "متن (انگلیسی)"})
    BodyAr = Column(Text, nullable=True, info={"label_fa": "متن (عربی)"})
    Rating = Column(Integer, nullable=True, info={"label_fa": "رتبه‌بندی"})
    IsApproved = Column(Boolean, nullable=False, default=False, info={"label_fa": "تایید شده"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    product = relationship('Products', backref='comments')
    parent = relationship('ProductComments', remote_side=[Id], backref='replies')


class Likes(Base):
    __tablename__ = 'Likes'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    UserId = Column(String(36), nullable=False, info={"label_fa": "کاربر"})
    TargetType = Column(String(20), nullable=False, info={"label_fa": "نوع هدف"})  # 'Product' | 'Blog'
    TargetId = Column(String(36), nullable=False, info={"label_fa": "شناسه هدف"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})

    __table_args__ = (
        UniqueConstraint('UserId', 'TargetType', 'TargetId', name='UQ_Likes_User_Target'),
        Index('IX_Likes_Target', 'TargetType', 'TargetId'),
    )


class SiteContent(Base):
    """Model for storing dynamic site content sections"""
    __tablename__ = 'SiteContent'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    
    SectionKey = Column(String(100), nullable=False, unique=True, info={"label_fa": "کلید بخش"})
    SectionName = Column(String(255), nullable=False, info={"label_fa": "نام بخش"})
    
    # Main content fields
    Title = Column(String(500), nullable=True, info={"label_fa": "عنوان"})
    Subtitle = Column(String(500), nullable=True, info={"label_fa": "زیرعنوان"})
    Content = Column(Text, nullable=True, info={"label_fa": "محتوا"})
    ContentEn = Column(Text, nullable=True, info={"label_fa": "محتوا (انگلیسی)"})
    ContentAr = Column(Text, nullable=True, info={"label_fa": "محتوا (عربی)"})
    
    # Additional fields for different section types
    ImageUrl = Column(String(500), nullable=True, info={"label_fa": "آدرس تصویر"})
    VideoUrl = Column(String(500), nullable=True, info={"label_fa": "آدرس ویدیو"})
    LinkUrl = Column(String(500), nullable=True, info={"label_fa": "لینک"})
    LinkText = Column(String(255), nullable=True, info={"label_fa": "متن لینک"})
    
    # For contact info and other structured data
    Field1 = Column(String(500), nullable=True, info={"label_fa": "فیلد 1"})
    Field2 = Column(String(500), nullable=True, info={"label_fa": "فیلد 2"})
    Field3 = Column(String(500), nullable=True, info={"label_fa": "فیلد 3"})
    Field4 = Column(String(500), nullable=True, info={"label_fa": "فیلد 4"})
    
    # For JSON data (sliders, testimonials, services, etc.)
    JsonData = Column(Text, nullable=True, info={"label_fa": "داده JSON"})
    
    SortOrder = Column(Integer, nullable=False, default=0, info={"label_fa": "ترتیب نمایش"})
    IsActive = Column(Boolean, nullable=False, default=True, info={"label_fa": "فعال"})
    
    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})
    
    def __str__(self):
        return self.SectionName or self.SectionKey or str(self.Id)


class Orders(Base):
    """Order model for storing customer orders"""
    __tablename__ = 'Orders'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    
    # User association (can be null for guest orders, but typically set after account creation)
    UserId = Column(Integer, ForeignKey('users.id'), nullable=True, index=True, info={"label_fa": "کاربر"})
    
    # Order details
    OrderNumber = Column(String(50), unique=True, nullable=False, index=True, info={"label_fa": "شماره سفارش"})
    Status = Column(String(20), nullable=False, default='pending', info={"label_fa": "وضعیت"})  # pending, processing, completed, cancelled
    PaymentStatus = Column(String(20), nullable=False, default='pending', info={"label_fa": "وضعیت پرداخت"})  # pending, paid, failed, refunded
    PaymentMethod = Column(String(50), nullable=True, info={"label_fa": "روش پرداخت"})
    PaymentTransactionId = Column(String(255), nullable=True, info={"label_fa": "شناسه تراکنش"})
    
    # Customer information (stored even if user account exists for historical accuracy)
    CustomerName = Column(String(255), nullable=False, info={"label_fa": "نام مشتری"})
    CustomerPhone = Column(String(80), nullable=False, index=True, info={"label_fa": "تلفن مشتری"})
    CustomerEmail = Column(String(120), nullable=True, info={"label_fa": "ایمیل مشتری"})
    ShippingAddress = Column(Text, nullable=True, info={"label_fa": "آدرس ارسال"})
    
    # Financial information
    SubTotal = Column(Numeric(18, 2), nullable=False, info={"label_fa": "جمع جزء"})
    TaxAmount = Column(Numeric(18, 2), nullable=False, default=0, info={"label_fa": "مالیات"})
    ShippingCost = Column(Numeric(18, 2), nullable=False, default=0, info={"label_fa": "هزینه ارسال"})
    TotalAmount = Column(Numeric(18, 2), nullable=False, info={"label_fa": "مبلغ کل"})
    
    # Order notes
    Notes = Column(Text, nullable=True, info={"label_fa": "یادداشت"})
    
    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})
    
    # Relationships
    items = relationship('OrderItems', backref='order', cascade='all, delete-orphan')
    
    def __str__(self):
        return f"Order {self.OrderNumber}"


class OrderItems(Base):
    """Order items model for storing individual products in an order"""
    __tablename__ = 'OrderItems'
    Id = Column(String(36), primary_key=True, default=new_guid_str, info={"label_fa": "شناسه"})
    
    OrderId = Column(String(36), ForeignKey('Orders.Id'), nullable=False, index=True, info={"label_fa": "سفارش"})
    ProductId = Column(String(36), ForeignKey('Products.Id'), nullable=False, index=True, info={"label_fa": "محصول"})
    
    # Product snapshot (stored at time of order for historical accuracy)
    ProductTitle = Column(String(255), nullable=False, info={"label_fa": "عنوان محصول"})
    ProductSKU = Column(String(100), nullable=True, info={"label_fa": "کد محصول (SKU)"})
    ProductPrice = Column(Numeric(18, 2), nullable=False, info={"label_fa": "قیمت محصول"})
    
    # Order item details
    Quantity = Column(Numeric(18, 2), nullable=False, info={"label_fa": "تعداد"})
    UnitPrice = Column(Numeric(18, 2), nullable=False, info={"label_fa": "قیمت واحد"})
    TotalPrice = Column(Numeric(18, 2), nullable=False, info={"label_fa": "قیمت کل"})
    
    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False, info={"label_fa": "حذف شده"})
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, info={"label_fa": "تاریخ ایجاد"})
    CreatedBy = Column(String(36), nullable=True, info={"label_fa": "ایجاد کننده"})
    UpdatedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ ویرایش"})
    UpdatedBy = Column(String(36), nullable=True, info={"label_fa": "ویرایش کننده"})
    DeletedAt = Column(DateTime, nullable=True, info={"label_fa": "تاریخ حذف"})
    DeletedBy = Column(String(36), nullable=True, info={"label_fa": "حذف کننده"})
    
    # Relationships
    product = relationship('Products', backref='order_items')
    
    def __str__(self):
        return f"{self.ProductTitle} x {self.Quantity}"