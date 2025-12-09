"""
Cart Service
Business logic for shopping cart management (session-based)
"""
from typing import List, Dict, Any, Optional
from flask import session
from app.repositories.db import get_session
from app.repositories.product_repo import ProductRepository


class CartService:
    """Service for cart operations"""
    
    CART_SESSION_KEY = 'cart'
    
    def get_cart(self) -> List[Dict[str, Any]]:
        """Get current cart from session"""
        return session.get(self.CART_SESSION_KEY, [])
    
    def add_item(self, product_id: str, quantity: int = 1) -> bool:
        """Add item to cart"""
        cart = self.get_cart()
        
        # Check if product already in cart
        for item in cart:
            if item.get('product_id') == product_id:
                # Update quantity
                item['quantity'] = item.get('quantity', 0) + quantity
                session[self.CART_SESSION_KEY] = cart
                session.modified = True
                return True
        
        # Add new item
        cart.append({
            'product_id': product_id,
            'quantity': quantity
        })
        session[self.CART_SESSION_KEY] = cart
        session.modified = True
        return True
    
    def update_item_quantity(self, product_id: str, quantity: int) -> bool:
        """Update item quantity in cart"""
        if quantity <= 0:
            return self.remove_item(product_id)
        
        cart = self.get_cart()
        for item in cart:
            if item.get('product_id') == product_id:
                item['quantity'] = quantity
                session[self.CART_SESSION_KEY] = cart
                session.modified = True
                return True
        return False
    
    def remove_item(self, product_id: str) -> bool:
        """Remove item from cart"""
        cart = self.get_cart()
        cart = [item for item in cart if item.get('product_id') != product_id]
        session[self.CART_SESSION_KEY] = cart
        session.modified = True
        return True
    
    def clear_cart(self):
        """Clear all items from cart"""
        session.pop(self.CART_SESSION_KEY, None)
        session.modified = True
    
    def get_cart_with_products(self) -> List[Dict[str, Any]]:
        """Get cart items with full product details"""
        cart = self.get_cart()
        if not cart:
            return []
        
        cart_with_products = []
        with next(get_session()) as db:
            product_repo = ProductRepository(db)
            for item in cart:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                
                product = product_repo.get_by_id(product_id)
                if product and not product.IsDeleted and product.IsActive:
                    cart_with_products.append({
                        'product_id': product_id,
                        'quantity': quantity,
                        'product': product,
                        'subtotal': float(product.Price) * quantity
                    })
        
        return cart_with_products
    
    def get_cart_total(self) -> float:
        """Calculate cart total"""
        cart_items = self.get_cart_with_products()
        return sum(item['subtotal'] for item in cart_items)
    
    def get_cart_count(self) -> int:
        """Get total number of items in cart"""
        cart = self.get_cart()
        return sum(item.get('quantity', 0) for item in cart)
    
    def validate_cart(self):
        """Validate cart items (check stock, availability)"""
        cart = self.get_cart()
        if not cart:
            return False, "سبد خرید خالی است"
        
        with next(get_session()) as db:
            product_repo = ProductRepository(db)
            for item in cart:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                
                product = product_repo.get_by_id(product_id)
                if not product:
                    return False, f"محصول با شناسه {product_id} یافت نشد"
                
                if product.IsDeleted or not product.IsActive:
                    return False, f"محصول {product.Title} در دسترس نیست"
                
                if float(product.Stock) < quantity:
                    return False, f"موجودی محصول {product.Title} کافی نیست"
        
        return True, None

