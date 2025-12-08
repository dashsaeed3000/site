"""
Service for managing site content
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.models import SiteContent
import json


class SiteContentService:
    """Service for retrieving and managing site content"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_content_by_key(self, section_key: str) -> Optional[SiteContent]:
        """Get a single content section by its key"""
        return self.db.query(SiteContent).filter(
            SiteContent.SectionKey == section_key,
            SiteContent.IsActive == True,
            SiteContent.IsDeleted == False
        ).first()
    
    def get_all_content(self) -> Dict[str, SiteContent]:
        """Get all active content sections as a dictionary keyed by SectionKey"""
        contents = self.db.query(SiteContent).filter(
            SiteContent.IsActive == True,
            SiteContent.IsDeleted == False
        ).order_by(SiteContent.SortOrder).all()
        
        return {content.SectionKey: content for content in contents}
    
    def get_content_list(self, section_key_prefix: str = None) -> List[SiteContent]:
        """Get a list of content sections, optionally filtered by key prefix"""
        query = self.db.query(SiteContent).filter(
            SiteContent.IsActive == True,
            SiteContent.IsDeleted == False
        )
        
        if section_key_prefix:
            query = query.filter(SiteContent.SectionKey.like(f"{section_key_prefix}%"))
        
        return query.order_by(SiteContent.SortOrder).all()
    
    def parse_json_data(self, content: SiteContent) -> Optional[dict]:
        """Parse JsonData field if it exists"""
        if content.JsonData:
            try:
                return json.loads(content.JsonData)
            except (json.JSONDecodeError, TypeError):
                return None
        return None
