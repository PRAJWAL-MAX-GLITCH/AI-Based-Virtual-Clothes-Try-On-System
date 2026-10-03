from datetime import datetime, timezone

def create_user_document(name, email, password_hash):
    """
    Creates a standardized user document for MongoDB.
    Enforces 'user' role by default and sets metadata.
    """
    now = datetime.now(timezone.utc)
    return {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": "user",  # Defaults to user, not admin
        "profile_image": None,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login": None
    }

def serialize_user(user_doc):
    """
    Safely converts a MongoDB user document into a JSON-serializable dict.
    Removes the password_hash and converts ObjectId to string.
    """
    if not user_doc:
        return None
        
    return {
        "id": str(user_doc.get("_id")),
        "name": user_doc.get("name"),
        "email": user_doc.get("email"),
        "role": user_doc.get("role"),
        "is_active": user_doc.get("is_active"),
        "profile_image_path": user_doc.get("profile_image_path") or user_doc.get("profile_image"),
        "phone": user_doc.get("phone"),
        "location": user_doc.get("location")
    }
