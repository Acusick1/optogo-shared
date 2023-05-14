from pymongo import MongoClient
from pymongo.database import Database
from config import settings

CLUSTER_URI = \
    f"mongodb+srv://{settings.mdb_username}:{settings.mdb_password}@{settings.mdb_host}/?retryWrites=true&w=majority"


def get_db(**kwargs) -> Database:

    try:
        db = MongoClient(CLUSTER_URI, **kwargs)[settings.mdb_name]
        return db
    except Exception as e:
        # Only here for testing without internet
        print(e)
