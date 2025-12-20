from typing import List, Optional
from sqlalchemy.orm import Session
from ..repositories.blog_repo import get_published_blogs, get_blog_by_slug
from ..models.models import Blogs


class BlogService:
    def __init__(self, db: Session):
        self.db = db

    def list_published(self, limit: int = 6) -> List[Blogs]:
        return get_published_blogs(self.db, limit=limit)

    def get_by_slug(self, slug: str) -> Optional[Blogs]:
        return get_blog_by_slug(self.db, slug)
