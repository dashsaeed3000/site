import pytest
from app.models.models import Product
from app.repositories.product_repo import ProductRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base


@pytest.fixture(scope='module')
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_create_and_list_products(in_memory_db):
    repo = ProductRepository(in_memory_db)
    p = repo.create(name='Test', slug='test', description='d', price=1.0, image='')
    assert p.id is not None
    products = repo.list_products()
    assert len(products) == 1
