from typing import List, Optional
from sqlalchemy.orm import Session
from ..repositories.blog_comment_repo import BlogCommentRepository
from ..models.models import BlogComments as Comment


class BlogCommentService:
    def __init__(self, db: Session):
        self.repo = BlogCommentRepository(db)

    def get_blog_comments(self, blog_id: str, approved_only: bool = True) -> List[Comment]:
        return self.repo.get_blog_comments(blog_id, approved_only=approved_only)

    def get_comment_replies(self, parent_id: str, approved_only: bool = True) -> List[Comment]:
        return self.repo.get_comment_replies(parent_id, approved_only=approved_only)

    def create_comment(self, blog_id: str, body: str, parent_id: str = None, user_id: str = None) -> Comment:
        return self.repo.create_comment(
            BlogId=blog_id,
            Body=body,
            ParentId=parent_id,
            UserId=user_id,
            IsApproved=False
        )
