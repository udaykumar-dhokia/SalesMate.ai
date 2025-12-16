from datetime import datetime
from config.db import db

class User:
    def __init__(self, email, password, full_name, mobile_number, telegram_chat_id=None):
        self.email = email
        self.password = password
        self.full_name = full_name
        self.mobile_number = mobile_number
        self.telegram_chat_id = telegram_chat_id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "full_name": self.full_name,
            "mobile_number": self.mobile_number,
            "telegram_chat_id": self.telegram_chat_id,
            "created_at": self.created_at
        }
