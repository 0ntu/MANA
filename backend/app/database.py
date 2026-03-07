import os
from pymongo import MongoClient, ASCENDING, DESCENDING

mongo_url = os.getenv("URL", "mongodb://localhost:**") #localhost url
connection = MongoClient(mongo_url)
mongo_database = os.getenv("DATABASE", *name*) #need database name
database = connection[mongo_database]

users = database["users"]
energy_logs = database["energy_logs"]
tasks = database["tasks"]

def initialize_indexes() -> None:
    users.create_index([("username", ASCENDING)], unique=True)                         #abc
    energy_logs.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])      #123 654
    tasks.create_index([("user_id", ASCENDING), ("scheduled_time", ASCENDING)])        #123 456
    tasks.create_index([("user_id", ASCENDING), ("status", ASCENDING)])                #123 abc
