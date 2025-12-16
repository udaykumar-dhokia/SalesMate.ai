
from langchain.tools import tool
from features.inventory.service import InventoryService

inventory_service = InventoryService()

@tool
def search_inventory(query: str = None, category: str = None, min_price: float = None, max_price: float = None):
    """
    Searches the product inventory for items matching the criteria.
    Use this tool when the user asks about available products, stock, or specific items.
    
    Args:
        query: Search term for product name, description, or subcategory (e.g., "shirt", "denim").
        category: Main category filter (e.g., "Men", "Women", "Accessories").
        min_price: Minimum price filter.
        max_price: Maximum price filter.
        
    Returns:
        A list of products matching the criteria.
    """
    results = inventory_service.search_products(query, category, min_price, max_price)
    if not results:
        return "No products found matching the criteria."
    return str(results)
