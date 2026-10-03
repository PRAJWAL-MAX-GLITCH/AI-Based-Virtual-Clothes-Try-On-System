import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.extensions import mongo
from app.models.user_clothing import serialize_user_clothing
from app.models.clothing import normalize_category, SUPPORTED_CATEGORIES
from app.services.upload_service import delete_image
from app.utils.validators import validate_name

class UserClothingServiceError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

def create_user_clothing(user_id, data, image_path):
    category = normalize_category(data.get('category'))
    if category not in SUPPORTED_CATEGORIES:
        # Delete image if validation fails
        delete_image(image_path)
        raise UserClothingServiceError("Unsupported category", "INVALID_CATEGORY")
        
    name = data.get('name')
    if name and not validate_name(name):
        delete_image(image_path)
        raise UserClothingServiceError("Invalid name length", "INVALID_NAME")
        
    now = datetime.datetime.now(datetime.timezone.utc)
    
    doc = {
        "user_id": ObjectId(user_id),
        "name": name.strip() if name else f"Custom {category.title()}",
        "category": category,
        "image": image_path,
        "available": True,
        "created_at": now,
        "updated_at": now
    }
    
    col = mongo.get_collection('user_clothing')
    result = col.insert_one(doc)
    doc['_id'] = result.inserted_id
    
    return serialize_user_clothing(doc)

def get_user_clothing_list(user_id):
    col = mongo.get_collection('user_clothing')
    cursor = col.find({"user_id": ObjectId(user_id), "available": True}).sort("created_at", -1)
    return [serialize_user_clothing(doc) for doc in cursor]

def get_user_clothing_by_id(user_id, clothing_id):
    try:
        obj_id = ObjectId(clothing_id)
    except InvalidId:
        raise UserClothingServiceError("Invalid clothing ID", "INVALID_ID")
        
    col = mongo.get_collection('user_clothing')
    
    # Crucial security check: Enforce user_id ownership
    doc = col.find_one({"_id": obj_id, "user_id": ObjectId(user_id)})
    
    if not doc:
        raise UserClothingServiceError("Clothing item not found or unauthorized", "CLOTHING_NOT_FOUND")
        
    return serialize_user_clothing(doc)

def delete_user_clothing(user_id, clothing_id):
    try:
        obj_id = ObjectId(clothing_id)
    except InvalidId:
        raise UserClothingServiceError("Invalid clothing ID", "INVALID_ID")
        
    col = mongo.get_collection('user_clothing')
    
    # Crucial security check: Enforce user_id ownership before delete
    doc = col.find_one({"_id": obj_id, "user_id": ObjectId(user_id)})
    
    if not doc:
        raise UserClothingServiceError("Clothing item not found or unauthorized", "CLOTHING_NOT_FOUND")
        
    # Physically delete the record and image to free up space (user specific)
    col.delete_one({"_id": obj_id})
    if doc.get('image'):
        delete_image(doc['image'])
