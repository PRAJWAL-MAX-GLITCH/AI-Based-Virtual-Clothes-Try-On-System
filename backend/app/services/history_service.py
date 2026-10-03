"""
app/services/history_service.py

Service layer for Try-On History & Result Management.
"""

import os
from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.extensions import mongo

class HistoryServiceError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)

def get_history(current_user: dict, page: int = 1, limit: int = 20) -> dict:
    """
    Retrieve paginated try-on history for the authenticated user.
    """
    db = mongo.get_db()
    
    # Safe pagination constraints
    page = max(1, page)
    limit = max(1, min(100, limit))
    skip = (page - 1) * limit
    
    query = {"user_id": ObjectId(current_user["id"])}
    
    total = db.tryon_history.count_documents(query)
    
    # Retrieve sorted by newest first
    cursor = db.tryon_history.find(query).sort("created_at", -1).skip(skip).limit(limit)
    
    items = []
    for record in cursor:
        items.append({
            "id": str(record["_id"]),
            "clothing_id": str(record.get("clothing_id")),
            "clothing_name": record.get("clothing_name"),
            "clothing_category": record.get("clothing_category"),
            "clothing_source": record.get("clothing_source"),
            "result_image": record.get("result_image"),
            "status": record.get("status", "completed"),
            "created_at": record.get("created_at").isoformat() if record.get("created_at") else None
        })
        
    pages = max(1, (total + limit - 1) // limit)
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages
        }
    }

def get_single_history(history_id_str: str, current_user: dict) -> dict:
    """
    Retrieve a specific history record for the authenticated user.
    """
    try:
        history_id = ObjectId(history_id_str)
    except InvalidId:
        raise HistoryServiceError("Invalid history ID", "INVALID_ID")
        
    db = mongo.get_db()
    record = db.tryon_history.find_one({"_id": history_id, "user_id": ObjectId(current_user["id"])})
    
    if not record:
        raise HistoryServiceError("History record not found", "NOT_FOUND")
        
    return {
        "id": str(record["_id"]),
        "person_image_id": record.get("person_image_id"),
        "clothing_id": str(record.get("clothing_id")),
        "clothing_name": record.get("clothing_name"),
        "clothing_category": record.get("clothing_category"),
        "clothing_source": record.get("clothing_source"),
        "result_image": record.get("result_image"),
        "status": record.get("status", "completed"),
        "created_at": record.get("created_at").isoformat() if record.get("created_at") else None
    }

def delete_history(history_id_str: str, current_user: dict) -> dict:
    """
    Delete a history record and its associated result image safely.
    Never deletes original person or clothing images.
    """
    try:
        history_id = ObjectId(history_id_str)
    except InvalidId:
        raise HistoryServiceError("Invalid history ID", "INVALID_ID")
        
    db = mongo.get_db()
    record = db.tryon_history.find_one({"_id": history_id, "user_id": ObjectId(current_user["id"])})
    
    if not record:
        raise HistoryServiceError("History record not found", "NOT_FOUND")
        
    # Safely delete the result image
    result_image_rel = record.get("result_image")
    if result_image_rel and result_image_rel.startswith("results/"):
        upload_root = current_app.config['UPLOAD_FOLDER']
        result_abs_path = os.path.join(upload_root, os.path.normpath(result_image_rel))
        
        # Verify it's safely within results directory
        if os.path.abspath(result_abs_path).startswith(os.path.abspath(os.path.join(upload_root, "results"))):
            if os.path.exists(result_abs_path):
                try:
                    os.remove(result_abs_path)
                    current_app.logger.info(f"Deleted result image: {result_abs_path}")
                except Exception as e:
                    current_app.logger.warning(f"Failed to delete result image {result_abs_path}: {e}")
            else:
                current_app.logger.warning(f"Result image already missing when deleting history: {result_abs_path}")
        else:
            current_app.logger.warning(f"Safety constraint prevented deletion of result path: {result_abs_path}")
            
    # Delete the document
    db.tryon_history.delete_one({"_id": history_id})
    current_app.logger.info(f"Deleted tryon_history record {history_id_str} for user {current_user['id']}")
    
    return {"message": "History deleted successfully"}

def get_history_result(history_id_str: str, current_user: dict) -> dict:
    """
    Get secure access to the result image associated with a history record.
    Replaces the temporary get_tryon_result mechanism.
    """
    try:
        history_id = ObjectId(history_id_str)
    except InvalidId:
        raise HistoryServiceError("Invalid history ID", "INVALID_ID")
        
    db = mongo.get_db()
    record = db.tryon_history.find_one({"_id": history_id, "user_id": ObjectId(current_user["id"])})
    
    if not record:
        raise HistoryServiceError("History record not found", "NOT_FOUND")
        
    relative_path = record.get("result_image")
    if not relative_path:
        raise HistoryServiceError("No result image associated with this history", "NO_RESULT_IMAGE")
        
    # Build URL (stub mechanism)
    url = f"/api/v1/static/{relative_path.replace(chr(92), '/')}"
    
    return {
        "history_id": str(record["_id"]),
        "result_image": relative_path,
        "url": url,
        "clothing_name": record.get("clothing_name")
    }
