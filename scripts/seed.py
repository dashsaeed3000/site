"""Seed script to create sample products and a test user."""
from app.repositories.db import engine_factory
from app.models.models import Base, Products, BlogCategories
from app.repositories.db import get_session


def run():
    engine = engine_factory()
    Base.metadata.create_all(bind=engine)
    with next(get_session()) as db:
        # add sample categories
        if not db.query(BlogCategories).count():
            cat = BlogCategories(Title='News', Slug='news')
            db.add(cat)
            db.commit()

        # add sample products
        if not db.query(Products).count():
            products = [
                Products(Title='Alpha Wallet', Slug='alpha-wallet', Description='Handmade leather wallet', Price=49.99, Stock=10, MainImageUrl='img/slider/1.jpg'),
                Products(Title='Beta Belt', Slug='beta-belt', Description='Genuine leather belt', Price=29.99, Stock=25, MainImageUrl='img/slider/2.jpg'),
                Products(Title='Gamma Bag', Slug='gamma-bag', Description='Premium leather bag', Price=149.99, Stock=5, MainImageUrl='img/slider/3.jpg'),
            ]
            db.add_all(products)
            db.commit()


if __name__ == '__main__':
    run()
