"""
Order Service
Business logic for orders
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.order_repo import OrderRepository
from app.repositories.product_repo import ProductRepository
from app.models.models import Orders, OrderItems, Products
import random
import string


class OrderService:
    """Service for order operations"""
    
    def __init__(self, db: Session):
        self.repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
    
    def generate_order_number(self) -> str:
        """Generate a unique order number"""
        # Format: ORD-YYYYMMDD-XXXXXX (6 random alphanumeric)
        from datetime import datetime
        date_str = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"ORD-{date_str}-{random_str}"
    
    def create_order_from_cart(
        self,
        cart_items: List[Dict[str, Any]],
        customer_name: str,
        customer_phone: str,
        customer_email: str = None,
        shipping_address: str = None,
        user_id: int = None,
        notes: str = None
    ) -> Orders:
        """Create an order from cart items"""
        
        # Calculate totals
        subtotal = Decimal('0.00')
        tax_rate = Decimal('0.09')  # 9% tax (adjust as needed)
        
        # Validate products and calculate subtotal
        order_items_data = []
        for item in cart_items:
            product_id = item.get('product_id')
            quantity = Decimal(str(item.get('quantity', 1)))
            
            # Get product details
            product = self.product_repo.get_by_id(product_id)
            if not product or product.IsDeleted or not product.IsActive:
                raise ValueError(f"Product {product_id} not found or unavailable")
            
            # Check stock
            if Decimal(str(product.Stock)) < quantity:
                raise ValueError(f"Insufficient stock for product {product.Title}")
            
            unit_price = Decimal(str(product.Price))
            total_price = unit_price * quantity
            subtotal += total_price
            
            # Store item data
            order_items_data.append({
                'product_id': product_id,
                'product_title': product.Title,
                'product_sku': product.SKU,
                'product_price': float(product.Price),
                'quantity': float(quantity),
                'unit_price': float(unit_price),
                'total_price': float(total_price)
            })
        
        # Calculate tax and total
        tax_amount = subtotal * tax_rate
        shipping_cost = Decimal('0.00')  # Free shipping for now (can be configured)
        total_amount = subtotal + tax_amount + shipping_cost
        
        # Create order
        order_data = {
            'OrderNumber': self.generate_order_number(),
            'UserId': user_id,
            'CustomerName': customer_name,
            'CustomerPhone': customer_phone,
            'CustomerEmail': customer_email,
            'ShippingAddress': shipping_address,
            'SubTotal': float(subtotal),
            'TaxAmount': float(tax_amount),
            'ShippingCost': float(shipping_cost),
            'TotalAmount': float(total_amount),
            'Status': 'pending',
            'PaymentStatus': 'pending',
            'Notes': notes
        }
        
        order = self.repo.create(order_data)
        
        # Create order items
        for item_data in order_items_data:
            self.repo.create_item({
                'OrderId': order.Id,
                'ProductId': item_data['product_id'],
                'ProductTitle': item_data['product_title'],
                'ProductSKU': item_data['product_sku'],
                'ProductPrice': item_data['product_price'],
                'Quantity': item_data['quantity'],
                'UnitPrice': item_data['unit_price'],
                'TotalPrice': item_data['total_price']
            })
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Orders]:
        """Get order by ID"""
        return self.repo.get_by_id(order_id)
    
    def get_order_by_number(self, order_number: str) -> Optional[Orders]:
        """Get order by order number"""
        return self.repo.get_by_order_number(order_number)
    
    def get_user_orders(self, user_id: int, limit: int = 50) -> List[Orders]:
        """Get orders for a user"""
        return self.repo.get_by_user_id(user_id, limit)
    
    def get_orders_by_phone(self, phone: str, limit: int = 50) -> List[Orders]:
        """Get orders by phone number"""
        return self.repo.get_by_phone(phone, limit)
    
    def update_order_payment(
        self,
        order_id: str,
        transaction_id: str,
        payment_method: str
    ) -> Optional[Orders]:
        """Update order with payment information"""
        order = self.repo.update_payment_info(order_id, transaction_id, payment_method)
        if order:
            # Update order status to processing
            self.repo.update_status(order_id, 'processing', 'paid')
        return order
    
    def cancel_order(self, order_id: str) -> Optional[Orders]:
        """Cancel an order"""
        return self.repo.update_status(order_id, 'cancelled')

