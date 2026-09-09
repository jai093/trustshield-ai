"""
MongoDB Connection Verifier
Ensures the database and collections exist, creates them if missing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.config import get_settings
from app.services.mongo_store import MongoAnalyticsStore
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def verify_mongodb():
    """Verify MongoDB connection and create database if needed"""
    settings = get_settings()
    
    if not settings.mongodb_uri:
        print("❌ MONGODB_URI not configured in .env")
        return False
    
    print(f"🔗 Connecting to MongoDB: {settings.mongodb_uri[:50]}...")
    
    try:
        client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Create/verify database
        db = client[settings.mongodb_database]
        print(f"📦 Database: {settings.mongodb_database}")
        
        # Create collection if it doesn't exist
        if settings.mongodb_collection not in db.list_collection_names():
            db.create_collection(settings.mongodb_collection)
            print(f"✅ Created collection: {settings.mongodb_collection}")
        else:
            print(f"✅ Collection exists: {settings.mongodb_collection}")
        
        # Create indexes for performance
        collection = db[settings.mongodb_collection]
        collection.create_index("timestamp")
        collection.create_index("user_id")
        collection.create_index("risk_level")
        print("✅ Indexes created")
        
        # Show stats
        count = collection.count_documents({})
        print(f"📊 Total documents in collection: {count}")
        
        return True
        
    except ServerSelectionTimeoutError:
        print("❌ MongoDB connection failed - server not reachable")
        return False
    except Exception as exc:
        print(f"❌ MongoDB error: {exc}")
        return False

if __name__ == "__main__":
    success = verify_mongodb()
    sys.exit(0 if success else 1)
