from typing import List
from sqlalchemy.orm import Session
from ..repositories.comment_repo import CommentRepository
from ..models.models import ProductComments as Comment

class CommentService:
    def __init__(self, db: Session):
        self.repo = CommentRepository(db)

    def get_product_comments(self, product_id: str, approved_only: bool = True) -> List[Comment]:
        """Get all comments for a product"""
        return self.repo.get_product_comments(product_id, approved_only)

    def get_comment_replies(self, parent_id: str, approved_only: bool = True) -> List[Comment]:
        """Get replies to a comment"""
        return self.repo.get_comment_replies(parent_id, approved_only)

    def create_comment(self, product_id: str, body: str, parent_id: str = None, user_id: str = None, rating: int = None) -> Comment:
        """Create a new comment"""
        return self.repo.create_comment(
            ProductId=product_id,
            Body=body,
            ParentId=parent_id,
            UserId=user_id,
            Rating=rating,
            IsApproved=False  # Comments need approval by default
        )
