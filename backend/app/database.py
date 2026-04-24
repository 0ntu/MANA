import os
import random
from datetime import datetime, timezone, timedelta, time
from zoneinfo import ZoneInfo
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


def seed_dummy_data() -> None:
    # create dummy users, energy logs, and tasks if not already seeded
    from app.authentication import hash_password

    if users.find_one({"_seeded": True}):
        return

    est = ZoneInfo("America/New_York")
    rng = random.Random(42)

    # --- dummy users ---
    dummy_users = [
        {"username": "alice", "energy_base": 7.0},
        {"username": "bob", "energy_base": 5.0},
        {"username": "carol", "energy_base": 8.0},
        {"username": "dave", "energy_base": 4.5},
        {"username": "eve", "energy_base": 6.0},
        {"username": "frank", "energy_base": 3.5},
        {"username": "grace", "energy_base": 7.5},
        {"username": "hank", "energy_base": 6.5},
        {"username": "iris", "energy_base": 5.5},
        {"username": "jack", "energy_base": 8.5},
    ]

    task_titles = [
        ("Study for Algorithms exam", 6.0),
        ("Grocery shopping", 2.0),
        ("Workout at gym", 4.5),
        ("Read chapter 5", 3.0),
        ("Group project meeting", 3.5),
        ("Laundry", 1.5),
        ("Cook dinner", 2.5),
        ("Office hours with TA", 2.0),
        ("Clean apartment", 3.0),
        ("Write lab report", 5.0),
        ("Call parents", 1.0),
        ("Practice piano", 2.5),
        ("Review lecture notes", 3.5),
        ("Submit homework", 4.0),
        ("Dentist appointment", 2.0),
        ("Club meeting", 2.5),
        ("Meal prep for week", 3.5),
        ("Debug project code", 5.5),
        ("Walk the dog", 1.5),
        ("Meditate", 1.0),
    ]

    start_date = datetime(2026, 4, 27, tzinfo=est)
    end_date = datetime(2026, 5, 9, tzinfo=est)
    num_days = (end_date - start_date).days + 1  # 13 days

    hashed_pw = hash_password("password123")

    for u in dummy_users:
        user_doc = {
            "username": u["username"],
            "hashed_pass": hashed_pw,
            "created_time": datetime.now(est),
            "current_energy": round(u["energy_base"] + rng.uniform(-1.0, 1.0), 1),
            "_seeded": True,
        }
        result = users.insert_one(user_doc)
        uid = result.inserted_id

        # --- energy logs: ~20-25 per user (spread across the date range) ---
        energy = u["energy_base"]
        for day_offset in range(num_days):
            day = start_date + timedelta(days=day_offset)
            # 1-3 logs per day, not every day
            if rng.random() < 0.3:
                continue
            num_logs = rng.randint(1, 3)
            for _ in range(num_logs):
                hour = rng.randint(7, 22)
                minute = rng.randint(0, 59)
                log_time = day.replace(hour=hour, minute=minute, second=0)
                energy = round(max(0.5, min(10.0, energy + rng.uniform(-2.0, 2.0))), 1)
                energy_logs.insert_one({
                    "user_id": uid,
                    "energy_level": energy,
                    "created_time": log_time,
                    "source": "manual",
                })

        users.update_one({"_id": uid}, {"$set": {"current_energy": energy}})

        # --- tasks: 3-5 per user per day across the range ---
        for day_offset in range(num_days):
            day = start_date + timedelta(days=day_offset)
            num_tasks = rng.randint(3, 5)
            chosen = rng.sample(task_titles, num_tasks)
            for title, base_cost in chosen:
                hour = rng.randint(8, 20)
                minute = rng.choice([0, 15, 30, 45])
                sched = day.replace(hour=hour, minute=minute, second=0)
                cost = round(max(0.5, min(10.0, base_cost + rng.uniform(-1.0, 1.0))), 1)
                is_past = sched < datetime.now(est)
                status_val = rng.choice(["completed", "planned"]) if is_past else "planned"
                tasks.insert_one({
                    "user_id": uid,
                    "title": title,
                    "description": "",
                    "scheduled_time": sched,
                    "energy_cost": cost,
                    "actual_energy_cost": cost if status_val == "completed" else None,
                    "status": status_val,
                    "created_time": sched - timedelta(hours=rng.randint(1, 48)),
                    "updated_time": None,
                    "completed_time": sched + timedelta(minutes=rng.randint(30, 120)) if status_val == "completed" else None,
                    "is_recurring": False,
                    "repeat_pattern": None,
                    "parent_task_id": None,
                    "is_generated_instance": False,
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
