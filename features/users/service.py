
import bcrypt
from config.db import db
from features.users.models import User

class AuthService:
    def __init__(self):
        self.collection = db["users"]

    def create_user(self, email, password, full_name, mobile_number, telegram_chat_id=None):
        if self.collection.find_one({"email": email}):
            raise ValueError("User already exists")
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(email, hashed_password.decode('utf-8'), full_name, mobile_number, telegram_chat_id)
        
        result = self.collection.insert_one(user.to_dict())
        return result.inserted_id

    def authenticate_user(self, email, password):
        user_data = self.collection.find_one({"email": email})
        if not user_data:
            return False
            
        if bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
            return user_data
        return False
        
    def link_telegram_id(self, email, telegram_chat_id):
        result = self.collection.update_one(
            {"email": email},
            {"$set": {"telegram_chat_id": telegram_chat_id}}
        )
        return result.modified_count > 0

    def get_user_by_telegram_id(self, telegram_chat_id):
        return self.collection.find_one({"telegram_chat_id": telegram_chat_id})
