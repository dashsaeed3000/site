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
    CategoryId = Column(String(36), ForeignKey('Categories.Id'), nullable=True)

    SKU = Column(String(100), nullable=True, unique=True)

    Title = Column(String(255), nullable=False)
    TitleEn = Column(String(255), nullable=True)
    TitleAr = Column(String(255), nullable=True)

    Slug = Column(String(255), nullable=False)
    SlugEn = Column(String(255), nullable=True)
    SlugAr = Column(String(255), nullable=True)

    ShortDescription = Column(String(1000), nullable=True)
    ShortDescriptionEn = Column(String(1000), nullable=True)
    ShortDescriptionAr = Column(String(1000), nullable=True)

    Description = Column(Text, nullable=True)
    DescriptionEn = Column(Text, nullable=True)
    DescriptionAr = Column(Text, nullable=True)

    Price = Column(Numeric(18, 2), nullable=False)
    Stock = Column(Numeric(18, 2), nullable=False, default=0)

    IsActive = Column(Boolean, nullable=False, default=True)
    IsFeatured = Column(Boolean, nullable=False, default=False)

    MainImageUrl = Column(String(500), nullable=True)
    MetaTitle = Column(String(255), nullable=True)
    MetaDescription = Column(String(500), nullable=True)
    MetaKeywords = Column(String(500), nullable=True)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column(String(36), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedBy = Column(String(36), nullable=True)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)

    category = relationship('Categories', backref='products')

    def __str__(self):
        return self.Title or str(self.Id)

    def __str__(self):
        # Used by Flask-Admin to show a readable label in dropdowns
        return self.Title or str(self.Id)


class ProductImages(Base):
    __tablename__ = 'ProductImages'
    Id = Column(String(36), primary_key=True, default=new_guid_str)
    ProductId = Column(String(36), ForeignKey('Products.Id'), nullable=False)

    ImageUrl = Column(String(500), nullable=False)
    AltText = Column(String(255), nullable=True)
    AltTextEn = Column(String(255), nullable=True)
    AltTextAr = Column(String(255), nullable=True)

    IsPrimary = Column(Boolean, nullable=False, default=False)
    SortOrder = Column(Integer, nullable=False, default=0)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column(String(36), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedBy = Column(String(36), nullable=True)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)

    product = relationship('Products', backref='images')


class BlogCategories(Base):
    __tablename__ = 'BlogCategories'
    Id = Column(String(36), primary_key=True, default=new_guid_str)

    Title = Column(String(255), nullable=False)
    TitleEn = Column(String(255), nullable=True)
    TitleAr = Column(String(255), nullable=True)

    Slug = Column(String(255), nullable=False)
    SlugEn = Column(String(255), nullable=True)
    SlugAr = Column(String(255), nullable=True)

    Description = Column(Text, nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column(String(36), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedBy = Column(String(36), nullable=True)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)


class Blogs(Base):
    __tablename__ = 'Blogs'
    Id = Column(String(36), primary_key=True, default=new_guid_str)
    BlogCategoryId = Column(String(36), ForeignKey('BlogCategories.Id'), nullable=True)
    AuthorId = Column(String(36), nullable=True)

    Title = Column(String(255), nullable=False)
    TitleEn = Column(String(255), nullable=True)
    TitleAr = Column(String(255), nullable=True)

    Slug = Column(String(255), nullable=False)
    SlugEn = Column(String(255), nullable=True)
    SlugAr = Column(String(255), nullable=True)

    Excerpt = Column(String(1000), nullable=True)
    ExcerptEn = Column(String(1000), nullable=True)
    ExcerptAr = Column(String(1000), nullable=True)

    Body = Column(Text, nullable=True)
    BodyEn = Column(Text, nullable=True)
    BodyAr = Column(Text, nullable=True)

    FeaturedImageUrl = Column(String(500), nullable=True)
    IsPublished = Column(Boolean, nullable=False, default=False)
    PublishedAt = Column(DateTime, nullable=True)
    Views = Column(Integer, nullable=False, default=0)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column(String(36), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedBy = Column(String(36), nullable=True)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)

    category = relationship('BlogCategories', backref='blogs')


class BlogComments(Base):
    __tablename__ = 'BlogComments'
    Id = Column(String(36), primary_key=True, default=new_guid_str)
    BlogId = Column(String(36), ForeignKey('Blogs.Id'), nullable=False)
    ParentId = Column(String(36), ForeignKey('BlogComments.Id'), nullable=True)
    UserId = Column(String(36), nullable=True)

    Body = Column(Text, nullable=False)
    BodyEn = Column(Text, nullable=True)
    BodyAr = Column(Text, nullable=True)
    IsApproved = Column(Boolean, nullable=False, default=False)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column(String(36), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedBy = Column(String(36), nullable=True)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)

    blog = relationship('Blogs', backref='comments')
    parent = relationship('BlogComments', remote_side=[Id], backref='replies')


class ProductComments(Base):
    __tablename__ = 'ProductComments'
    Id = Column(String(36), primary_key=True, default=new_guid_str)
    ProductId = Column(String(36), ForeignKey('Products.Id'), nullable=False)
    ParentId = Column(String(36), ForeignKey('ProductComments.Id'), nullable=True)
    UserId = Column(String(36), nullable=True)

    Body = Column(Text, nullable=False)
    BodyEn = Column(Text, nullable=True)
    BodyAr = Column(Text, nullable=True)
    Rating = Column(Integer, nullable=True)
    IsApproved = Column(Boolean, nullable=False, default=False)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column(String(36), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedBy = Column(String(36), nullable=True)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)

    product = relationship('Products', backref='comments')
    parent = relationship('ProductComments', remote_side=[Id], backref='replies')


class Likes(Base):
    __tablename__ = 'Likes'
    Id = Column(String(36), primary_key=True, default=new_guid_str)
    UserId = Column(String(36), nullable=False)
    TargetType = Column(String(20), nullable=False)  # 'Product' | 'Blog'
    TargetId = Column(String(36), nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Audit + soft delete
    IsDeleted = Column(Boolean, nullable=False, default=False)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(String(36), nullable=True)

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
