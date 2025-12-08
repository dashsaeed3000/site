import pytest
from app.repositories.db import engine_factory
from app.models.models import Base, Product, User
from app.repositories.db import get_session
from app.utils.security import hash_password

@pytest.fixture(scope='module')
def setup_db():
    engine = engine_factory()
    Base.metadata.create_all(bind=engine)
    # use real DB configured in env; this test meant as integration if DB available
    yield

def test_seed_and_products(setup_db):
    with next(get_session()) as db:
        if not db.query(Product).count():
            p = Product(name='IntTest', slug='int-test', description='int', price=12.5)
            db.add(p)
            db.commit()
        assert db.query(Product).count() >= 1
