
from config.db import db
import re

class InventoryService:
    def __init__(self):
        self.collection = db["inventory"]

    def search_products(self, query=None, category=None, min_price=None, max_price=None, limit=10):
        filter_query = {}
        
        if query:
            regex = re.compile(query, re.IGNORECASE)
            filter_query["$or"] = [
                {"name": regex},
                {"description": regex},
                {"subcategory": regex}
            ]
            
        if category:
            filter_query["category"] = re.compile(category, re.IGNORECASE)
            
        if min_price is not None or max_price is not None:
            price_query = {}
            if min_price is not None:
                price_query["$gte"] = float(min_price)
            if max_price is not None:
                price_query["$lte"] = float(max_price)
            filter_query["price"] = price_query

        cursor = self.collection.find(filter_query).limit(limit)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"]) 
            results.append(doc)
            
        return results
