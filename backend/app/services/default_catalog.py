import datetime
from app.extensions import mongo

DEFAULT_CLOTHING_ITEMS = [
    {
        "name": "Black Formal Shirt",
        "category": "shirt",
        "description": "Premium black long-sleeve button-up formal shirt. Tailored fit for business and evening wear.",
        "price": 1499,
        "color": "Black",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/black_shirt.jpg",
        "available": True,
    },
    {
        "name": "White Cotton T-Shirt",
        "category": "t-shirt",
        "description": "Essential crew-neck t-shirt crafted from 100% breathable organic combed cotton.",
        "price": 699,
        "color": "White",
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "image": "clothing/catalog/white_tshirt.jpg",
        "available": True,
    },
    {
        "name": "Heather Grey Crew Tee",
        "category": "t-shirt",
        "description": "Soft heather grey casual crew-neck t-shirt with premium ribbed collar.",
        "price": 749,
        "color": "Grey",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/grey_tshirt.jpg",
        "available": True,
    },
    {
        "name": "Navy Fleece Hoodie",
        "category": "hoodie",
        "description": "Heavyweight navy blue fleece pullover hoodie with kangaroo pouch pocket and metal-tipped drawstrings.",
        "price": 1999,
        "color": "Navy",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "image": "clothing/catalog/navy_hoodie.jpg",
        "available": True,
    },
    {
        "name": "Classic Blue Denim Jacket",
        "category": "jacket",
        "description": "Vintage wash blue denim trucker jacket with dual chest flap pockets and copper button closures.",
        "price": 2799,
        "color": "Blue",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/blue_denim_jacket.jpg",
        "available": True,
    },
    {
        "name": "Crimson Streetwear Hoodie",
        "category": "hoodie",
        "description": "Vibrant crimson red relaxed-fit hoodie with soft brushed interior and clean minimalist finish.",
        "price": 1899,
        "color": "Red",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/red_hoodie.jpg",
        "available": True,
    },
    {
        "name": "Emerald Summer Midi Dress",
        "category": "dress",
        "description": "Elegant emerald green linen-blend summer midi dress with ruffled hem and waist tie belt.",
        "price": 2499,
        "color": "Green",
        "sizes": ["XS", "S", "M", "L"],
        "image": "clothing/catalog/green_dress.jpg",
        "available": True,
    },
    {
        "name": "Beige Cotton Bomber Jacket",
        "category": "jacket",
        "description": "Lightweight neutral beige zip-up bomber jacket with ribbed collar, hem, and cuffs.",
        "price": 2599,
        "color": "Beige",
        "sizes": ["S", "M", "L", "XL"],
        "image": "clothing/catalog/beige_jacket.jpg",
        "available": True,
    },
]

def ensure_default_catalog_seeded(app):
    """
    Checks if the clothing catalog in the active database has any items.
    If it is empty, automatically populates it with realistic, real-world catalog items.
    """
    with app.app_context():
        try:
            clothing_col = mongo.get_collection('clothing')
            count = clothing_col.count_documents({})
            if count == 0:
                app.logger.info("Clothing collection is empty. Auto-seeding default catalog...")
                now = datetime.datetime.now(datetime.timezone.utc)
                for item in DEFAULT_CLOTHING_ITEMS:
                    doc = dict(item)
                    doc["created_at"] = now
                    doc["updated_at"] = now
                    clothing_col.insert_one(doc)
                app.logger.info(f"Successfully seeded {len(DEFAULT_CLOTHING_ITEMS)} real-world clothing items.")
            else:
                # Also ensure all 8 default items exist even if partial
                now = datetime.datetime.now(datetime.timezone.utc)
                for item in DEFAULT_CLOTHING_ITEMS:
                    if not clothing_col.find_one({"name": item["name"]}):
                        doc = dict(item)
                        doc["created_at"] = now
                        doc["updated_at"] = now
                        clothing_col.insert_one(doc)
                        app.logger.info(f"Added missing catalog item: {item['name']}")
        except Exception as e:
            app.logger.warning(f"Could not auto-seed clothing catalog: {e}")
