import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
db = client["salesmate"]
