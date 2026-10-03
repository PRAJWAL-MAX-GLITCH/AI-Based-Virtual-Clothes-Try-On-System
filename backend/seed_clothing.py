"""
Seed script to add real clothing items to the catalog.
Run from the backend directory: python seed_clothing.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import mongo
import datetime

app = create_app('development')

ITEMS = [
    {
        "name": "Black Formal Shirt",
        "category": "shirt",
        "description": "Classic black long-sleeve button-up formal shirt. Perfect for office and evening wear.",
        "price": 1299,
        "color": "Black",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/black_shirt.jpg",
        "available": True,
    },
    {
        "name": "White Cotton T-Shirt",
        "category": "t-shirt",
        "description": "Everyday essential white crew-neck tee made from 100% premium cotton.",
        "price": 499,
        "color": "White",
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "image": "clothing/catalog/white_tshirt.jpg",
        "available": True,
    },
    {
        "name": "Heather Grey T-Shirt",
        "category": "t-shirt",
        "description": "Soft heather grey crew-neck t-shirt, lightweight and breathable.",
        "price": 549,
        "color": "Grey",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/grey_tshirt.jpg",
        "available": True,
    },
    {
        "name": "Navy Pullover Hoodie",
        "category": "hoodie",
        "description": "Cozy navy blue fleece pullover hoodie with kangaroo pocket.",
        "price": 1799,
        "color": "Navy",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "image": "clothing/catalog/navy_hoodie.jpg",
        "available": True,
    },
    {
        "name": "Blue Denim Jacket",
        "category": "jacket",
        "description": "Classic mid-wash blue denim trucker jacket with chest pockets.",
        "price": 2499,
        "color": "Blue",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/blue_denim_jacket.jpg",
        "available": True,
    },
]

with app.app_context():
    col = mongo.get_collection('clothing')
    now = datetime.datetime.now(datetime.timezone.utc)

    inserted = 0
    for item in ITEMS:
        # Avoid duplicates by name
        if col.find_one({"name": item["name"]}):
            print(f"  SKIP (already exists): {item['name']}")
            continue
        item["created_at"] = now
        item["updated_at"] = now
        col.insert_one(item)
        print(f"  INSERTED: {item['name']}")
        inserted += 1

    print(f"\nDone! {inserted} items inserted.")
