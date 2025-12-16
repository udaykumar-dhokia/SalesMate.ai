
import os
import sys
from datetime import datetime

# Add agent directory to sys.path to allow imports
sys.path.append(os.path.join(os.getcwd()))

from config.db import db

def seed_inventory():
    print("Seeding inventory...")
    collection = db["inventory"]
    
    # Sample data for a clothing brand
    # Categories: Men, Women, Accessories
    items = [
        # Men
        {
            "name": "Classic White T-Shirt",
            "category": "Men",
            "subcategory": "T-Shirts",
            "price": 25.00,
            "stock": 100,
            "description": "Premium cotton classic fit white t-shirt.",
            "sizes": ["S", "M", "L", "XL"],
            "created_at": datetime.utcnow()
        },
        {
            "name": "Slim Fit Denim Jeans",
            "category": "Men",
            "subcategory": "Jeans",
            "price": 65.00,
            "stock": 50,
            "description": "Dark wash slim fit denim jeans.",
            "sizes": ["30", "32", "34", "36"],
            "created_at": datetime.utcnow()
        },
        {
            "name": "Leather Jacket",
            "category": "Men",
            "subcategory": "Jackets",
            "price": 150.00,
            "stock": 20,
            "description": "Genuine leather biker jacket.",
            "sizes": ["M", "L", "XL"],
            "created_at": datetime.utcnow()
        },
        # Women
        {
            "name": "Floral Summer Dress",
            "category": "Women",
            "subcategory": "Dresses",
            "price": 45.00,
            "stock": 80,
            "description": "Lightweight floral print summer dress.",
            "sizes": ["XS", "S", "M", "L"],
            "created_at": datetime.utcnow()
        },
        {
            "name": "High-Waist Trousers",
            "category": "Women",
            "subcategory": "Pants",
            "price": 55.00,
            "stock": 60,
            "description": "Elegant high-waist trousers for work or casual wear.",
            "sizes": ["S", "M", "L"],
            "created_at": datetime.utcnow()
        },
        # Accessories
        {
            "name": "Unisex Canvas Sneaker",
            "category": "Accessories",
            "subcategory": "Shoes",
            "price": 40.00,
            "stock": 120,
            "description": "Comfortable canvas sneakers in various colors.",
            "sizes": ["38", "39", "40", "41", "42", "43", "44"],
            "created_at": datetime.utcnow()
        },
        {
            "name": "Leather Belt",
            "category": "Accessories",
            "subcategory": "Belts",
            "price": 20.00,
            "stock": 200,
            "description": "Classic leather belt with metal buckle.",
            "sizes": ["S", "M", "L", "XL"],
            "created_at": datetime.utcnow()
        }
    ]

    # Clear existing inventory to avoid duplicates if re-run (optional, or just insert)
    # collection.delete_many({}) 
    # For safe seeding, let's just insert new ones or check existence. 
    # Usually seeding implies fresh start or careful addition. I'll drop and recreate for "dummy" data request.
    
    collection.delete_many({})
    print("Cleared existing inventory.")
    
    result = collection.insert_many(items)
    print(f"Inserted {len(result.inserted_ids)} items into inventory.")

if __name__ == "__main__":
    seed_inventory()
