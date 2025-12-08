from typing import List
from sqlalchemy.orm import Session
from ..repositories.product_repo import ProductRepository
from ..models.models import Products as Product

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def list_products(self) -> List[Product]:
        return self.repo.list_products()

    def search_products(self, query: str) -> List[Product]:
        """Search products by query string"""
        return self.repo.search_products(query)

    def get_product(self, slug: str) -> Product:
        return self.repo.get_by_slug(slug)

    def create_product(self, **data) -> Product:
        return self.repo.create(**data)

    def update_product(self, product_id: int, **data) -> Product:
        p = self.repo.get_by_id(product_id)
        if not p:
            raise ValueError('Product not found')
        return self.repo.update(p, **data)

    def delete_product(self, product_id: int) -> None:
        p = self.repo.get_by_id(product_id)
        if not p:
            raise ValueError('Product not found')
        self.repo.delete(p)
