from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.models import BlogComments as Comment


class BlogCommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_blog_comments(self, blog_id: str, approved_only: bool = True) -> List[Comment]:
        query = self.db.query(Comment).filter(
            Comment.BlogId == blog_id,
            Comment.IsDeleted == False,
            Comment.ParentId == None
        )
        if approved_only:
            query = query.filter(Comment.IsApproved == True)
        return query.order_by(Comment.CreatedAt.desc()).all()

    def get_comment_replies(self, parent_id: str, approved_only: bool = True) -> List[Comment]:
        query = self.db.query(Comment).filter(
            Comment.ParentId == parent_id,
            Comment.IsDeleted == False
        )
        if approved_only:
            query = query.filter(Comment.IsApproved == True)
        return query.order_by(Comment.CreatedAt.asc()).all()

    def create_comment(self, **data) -> Comment:
        comment = Comment(**data)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_id(self, comment_id: str) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.Id == comment_id).first()
