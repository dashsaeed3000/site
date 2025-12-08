from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.models import ProductComments as Comment

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_product_comments(self, product_id: str, approved_only: bool = True) -> List[Comment]:
        """Get all comments for a product, optionally only approved ones"""
        query = self.db.query(Comment).filter(
            Comment.ProductId == product_id,
            Comment.IsDeleted == False,
            Comment.ParentId == None  # Only top-level comments
        )
        if approved_only:
            query = query.filter(Comment.IsApproved == True)
        return query.order_by(Comment.CreatedAt.desc()).all()

    def get_comment_replies(self, parent_id: str, approved_only: bool = True) -> List[Comment]:
        """Get replies to a comment"""
        query = self.db.query(Comment).filter(
            Comment.ParentId == parent_id,
            Comment.IsDeleted == False
        )
        if approved_only:
            query = query.filter(Comment.IsApproved == True)
        return query.order_by(Comment.CreatedAt.asc()).all()

    def create_comment(self, **data) -> Comment:
        """Create a new comment"""
        comment = Comment(**data)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID"""
        return self.db.query(Comment).filter(Comment.Id == comment_id).first()
