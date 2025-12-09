"""
Order Repository
Data access layer for orders
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Orders, OrderItems


class OrderRepository:
    """Repository for order data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, order_data: dict) -> Orders:
        """Create a new order"""
        order = Orders(**order_data)
        self.db.add(order)
        self.db.flush()  # Flush to get the order ID
        return order
    
    def create_item(self, item_data: dict) -> OrderItems:
        """Create a new order item"""
        item = OrderItems(**item_data)
        self.db.add(item)
        return item
    
    def get_by_id(self, order_id: str) -> Optional[Orders]:
        """Get order by ID"""
        return self.db.query(Orders).filter(
            Orders.Id == order_id,
            Orders.IsDeleted == False
        ).first()
    
    def get_by_order_number(self, order_number: str) -> Optional[Orders]:
        """Get order by order number"""
        return self.db.query(Orders).filter(
            Orders.OrderNumber == order_number,
            Orders.IsDeleted == False
        ).first()
    
    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[Orders]:
        """Get orders for a user"""
        return self.db.query(Orders).filter(
            Orders.UserId == user_id,
            Orders.IsDeleted == False
        ).order_by(desc(Orders.CreatedAt)).limit(limit).all()
    
    def get_by_phone(self, phone: str, limit: int = 50) -> List[Orders]:
        """Get orders by customer phone number"""
        return self.db.query(Orders).filter(
            Orders.CustomerPhone == phone,
            Orders.IsDeleted == False
        ).order_by(desc(Orders.CreatedAt)).limit(limit).all()
    
    def update_status(self, order_id: str, status: str, payment_status: str = None) -> Optional[Orders]:
        """Update order status"""
        order = self.get_by_id(order_id)
        if order:
            order.Status = status
            if payment_status:
                order.PaymentStatus = payment_status
            self.db.flush()
        return order
    
    def update_payment_info(self, order_id: str, transaction_id: str, payment_method: str) -> Optional[Orders]:
        """Update payment information"""
        order = self.get_by_id(order_id)
        if order:
            order.PaymentTransactionId = transaction_id
            order.PaymentMethod = payment_method
            order.PaymentStatus = 'paid'
            self.db.flush()
        return order

