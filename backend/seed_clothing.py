"""
Seed script to add real clothing items to the catalog.
Can seed both local database and remote MongoDB Atlas.
Usage: python seed_clothing.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import mongo
from app.services.default_catalog import DEFAULT_CLOTHING_ITEMS
import datetime

# Check if Atlas URI is set or use default
atlas_uri = os.environ.get(
    'MONGO_URI',
    'mongodb://prajwalpatil282005_db_user:b8LicYVHb0Vg6x9W@ac-ycgtuc3-shard-00-00.qu5g1pa.mongodb.net:27017,ac-ycgtuc3-shard-00-01.qu5g1pa.mongodb.net:27017,ac-ycgtuc3-shard-00-02.qu5g1pa.mongodb.net:27017/virtual_try_on?ssl=true&replicaSet=atlas-10aeen-shard-0&authSource=admin&appName=Cluster0'
)
os.environ['MONGO_URI'] = atlas_uri

app = create_app('development')

with app.app_context():
    col = mongo.get_collection('clothing')
    now = datetime.datetime.now(datetime.timezone.utc)

    inserted = 0
    for item in DEFAULT_CLOTHING_ITEMS:
        existing = col.find_one({"name": item["name"]})
        if existing:
            # Update image path and details to ensure latest real images
            col.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "image": item["image"],
                    "description": item["description"],
                    "price": item["price"],
                    "color": item["color"],
                    "available": True,
                    "updated_at": now
                }}
            )
            print(f"  UPDATED: {item['name']}")
        else:
            doc = dict(item)
            doc["created_at"] = now
            doc["updated_at"] = now
            col.insert_one(doc)
            print(f"  INSERTED: {item['name']}")
            inserted += 1

    total = col.count_documents({})
    print(f"\nDone! {inserted} items inserted. Total catalog items in DB: {total}")
