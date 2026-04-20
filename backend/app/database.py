import os
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, DESCENDING

mongo_url = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://localhost:27017"))
connection = MongoClient(mongo_url)
mongo_database = os.getenv("DATABASE", "mana")
database = connection[mongo_database]

users = database["users"]
energy_logs = database["energy_logs"]
tasks = database["tasks"]


def create_admin() -> None:
    # create the admin account as it cannot be created via the signup page
    from app.authentication import hash_password  # local import to avoid circular

    admin_username = "admin"
    admin_password = "admin" # unguessable

    if not users.find_one({"role": "admin"}):
        users.insert_one({
            "username": admin_username,
            "hashed_pass": hash_password(admin_password),
            "created_time": datetime.now(timezone.utc),
            "current_energy": 0.0,
            "role": "admin",
        })


def initialize_indexes() -> None:
    users.create_index([("username", ASCENDING)], unique=True)
    users.create_index([("share_token", ASCENDING)], unique=True, sparse=True)
    energy_logs.create_index([("user_id", ASCENDING), ("created_time", DESCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("scheduled_time", ASCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("is_recurring", ASCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("parent_task_id", ASCENDING)])
    tasks.create_index([("user_id", ASCENDING), ("is_generated_instance", ASCENDING), ("scheduled_time", ASCENDING)])
