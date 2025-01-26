from pymongo import MongoClient
from pymongo.database import Database

from packages.config import global_settings

CLUSTER_URI = f"mongodb+srv://{global_settings.mdb_username}:{global_settings.mdb_password}@{global_settings.mdb_host}/?retryWrites=true&w=majority"


def get_db(**kwargs) -> Database:
    try:
        db = MongoClient(CLUSTER_URI, **kwargs)[global_settings.mdb_name]
        return db
    except Exception as e:
        # Only here for testing without internet
        print(e)
