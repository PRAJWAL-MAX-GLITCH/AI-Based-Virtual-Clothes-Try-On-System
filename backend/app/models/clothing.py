from datetime import datetime, timezone

SUPPORTED_CATEGORIES = {"t-shirt", "shirt", "hoodie", "jacket", "dress", "top"}

def normalize_category(category):
    if not category or not isinstance(category, str):
        return None
    # Normalize: lowercase, replace spaces and underscores with hyphens
    cat = category.lower().strip().replace(" ", "-").replace("_", "-")
    # specific normalizations
    if cat == "tshirt" or cat == "t-shirt":
        return "t-shirt"
    return cat

def serialize_clothing(doc):
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "description": doc.get("description"),
        "price": doc.get("price"),
        "color": doc.get("color"),
        "sizes": doc.get("sizes", []),
        "image": doc.get("image"),
        "available": doc.get("available", True),
        "created_by": str(doc.get("created_by")) if doc.get("created_by") else None,
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at")
    }
