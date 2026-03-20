import os
from pymongo import MongoClient, ASCENDING, DESCENDING

mongo_url = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://localhost:27017"))
connection = MongoClient(mongo_url)
mongo_database = os.getenv("DATABASE", "mana")
database = connection[mongo_database]

users = database["users"]
energy_logs = database["energy_logs"]
tasks = database["tasks"]


def initialize_indexes() -> None:
    users.create_index([("username", ASCENDING)], unique=True)
    energy_logs.create_index([("user_id", ASCENDING), ("created_time", DESCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("scheduled_time", ASCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
