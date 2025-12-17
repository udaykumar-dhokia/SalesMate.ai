
from langchain.tools import tool
from features.orders.service import OrderService
from features.notifications.service import EmailService
from features.inventory.service import InventoryService
from features.users.service import AuthService
import time
import asyncio

order_service = OrderService()
email_service = EmailService()
inventory_service = InventoryService()

@tool
def buy_product(product_name: str, quantity: int = 1, user_email: str = None):
    """
    Processes a product purchase.
    
    Args:
        product_name: The name of the product to buy.
        quantity: The number of items to purchase.
        user_email: The email address to send the receipt to. If not provided, it will ask or use a default.
    
    Returns:
        A confirmation message with order details or an error message.
    """
    
    products = inventory_service.search_products(query=product_name, limit=1)
    if not products:
        return f"Error: Product '{product_name}' not found."
    
    product = products[0]
    
    if product.get('stock', 0) < quantity:
        return f"Error: Insufficient stock for '{product['name']}'. Available: {product.get('stock', 0)}"

    price = product.get('price', 0)
    total_amount = price * quantity
    
    user_id = user_email if user_email else "guest_user"
    
    items = [{
        "name": product["name"],
        "quantity": quantity,
        "price": price,
        "image_url": product.get("image_url")
    }]
    
    order = order_service.create_order(user_id, items, total_amount)
    
    if user_email:
        email_service.send_order_confirmation(user_email, order)
        email_msg = f"Confirmation email sent to {user_email}."
    else:
        email_msg = "No email provided for notification."

    return (
        f"✅ Payment Successful!\n"
        f"Order Placed: #{order['order_id']}\n"
        f"Total: ${total_amount}\n"
        f"Payment ID: {order['payment_id']}\n"
        f"{email_msg}\n"
        f"Thank you for shopping with SalesMate!"
    )
