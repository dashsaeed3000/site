from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from ..models.models import Products as Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, limit: int = 100) -> List[Product]:
        """List active, non-deleted products with eager loading of category"""
        return self.db.query(Product).options(
            joinedload(Product.category)
        ).filter(
            Product.IsDeleted == False,
            Product.IsActive == True
        ).limit(limit).all()
    
    def search_products(self, query: str, limit: int = 50) -> List[Product]:
        """Search products by title, description, or SKU with eager loading of category"""
        search_term = f"%{query}%"
        return self.db.query(Product).options(
            joinedload(Product.category)
        ).filter(
            Product.IsDeleted == False,
            Product.IsActive == True,
            (
                Product.Title.like(search_term) |
                Product.ShortDescription.like(search_term) |
                Product.Description.like(search_term) |
                Product.SKU.like(search_term)
            )
        ).limit(limit).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.Id == product_id).first()

    def get_by_slug(self, slug: str) -> Optional[Product]:
        """Get product by slug with eager loading of images and category"""
        return self.db.query(Product).options(
            joinedload(Product.images),
            joinedload(Product.category)
        ).filter(Product.Slug == slug).first()

    def create(self, **data) -> Product:
        p = Product(**data)
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def update(self, product: Product, **data) -> Product:
        for k, v in data.items():
            # accept both camel and Pascal-style keys matching model attributes
            if hasattr(product, k):
                setattr(product, k, v)
            else:
                # try Title/Slug style
                setattr(product, k, v)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        # Soft delete pattern: set IsDeleted flag and DeletedAt
        product.IsDeleted = True
        from datetime import datetime
        product.DeletedAt = datetime.utcnow()
        self.db.add(product)
        self.db.commit()
