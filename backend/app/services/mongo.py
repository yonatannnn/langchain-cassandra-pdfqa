import os
from typing import Optional
from pymongo import MongoClient

_client: Optional[MongoClient] = None


def mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    return _client


def mongo_db():
    db_name = os.getenv("MONGODB_DB", "document_loader")
    return mongo_client()[db_name]
