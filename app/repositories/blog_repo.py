from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from ..models.models import Blogs


def get_published_blogs(db: Session, limit: int = 6) -> List[Blogs]:
    q = (
        db.query(Blogs)
        .options(joinedload(Blogs.category))
        .order_by(Blogs.CreatedAt.desc())
    )

    if limit:
        q = q.limit(limit)

    return q.all()


def get_blog_by_slug(db: Session, slug: str) -> Optional[Blogs]:
    return (
        db.query(Blogs)
        .options(joinedload(Blogs.category))
        .filter(Blogs.Slug == slug)
        .first()
    )
