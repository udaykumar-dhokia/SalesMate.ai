
from config.db import db
from datetime import datetime
import uuid

class OrderService:
    def __init__(self):
        self.collection = db["orders"]

    def create_order(self, user_id: str, items: list, total_amount: float, status: str = "paid"):
        """
        Creates a new order in the database.
        
        Args:
            user_id: The ID of the user placing the order.
            items: List of dictionaries containing product details (name, quantity, price, image_url).
            total_amount: Total price of the order.
            status: Status of the order (default: "paid").
            
        Returns:
            The newly created order document including the inserted ID.
        """
        order = {
            "order_id": str(uuid.uuid4()),
            "user_id": user_id,
            "items": items,
            "total_amount": total_amount,
            "status": status,
            "created_at": datetime.utcnow(),
            "payment_id": f"pay_{uuid.uuid4().hex[:12]}"
        }
        
        result = self.collection.insert_one(order)
        order["_id"] = result.inserted_id
        return order
