def serialize_user_clothing(doc):
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")),
        "user_id": str(doc.get("user_id")),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "image": doc.get("image"),
        "available": doc.get("available", True),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
        "type": "user_clothing"
    }
