import datetime
import re
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.extensions import mongo
from app.models.clothing import serialize_clothing, normalize_category, SUPPORTED_CATEGORIES
from app.utils.validators import validate_name, validate_price, validate_sizes

class ClothingServiceError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

def create_clothing(data, admin_id):
    name = data.get('name')
    raw_category = data.get('category')
    description = data.get('description', '')
    price = data.get('price')
    color = data.get('color')
    sizes = data.get('sizes')

    if not validate_name(name):
        raise ClothingServiceError("Invalid name", "INVALID_NAME")
    if not validate_price(price):
        raise ClothingServiceError("Invalid price", "INVALID_PRICE")
    if not color or not isinstance(color, str):
        raise ClothingServiceError("Invalid color", "INVALID_COLOR")
    if not validate_sizes(sizes):
        raise ClothingServiceError("Invalid sizes array", "INVALID_SIZES")

    category = normalize_category(raw_category)
    if category not in SUPPORTED_CATEGORIES:
        raise ClothingServiceError("Unsupported category", "INVALID_CATEGORY")

    now = datetime.datetime.now(datetime.timezone.utc)
    
    clothing_doc = {
        "name": name.strip(),
        "category": category,
        "description": description.strip() if isinstance(description, str) else "",
        "price": float(price),
        "color": color.strip().lower(),
        "sizes": [s.strip().upper() for s in sizes],
        "image": None,
        "available": data.get('available', True),
        "created_by": ObjectId(admin_id),
        "created_at": now,
        "updated_at": now
    }

    col = mongo.get_collection('clothing')
    result = col.insert_one(clothing_doc)
    clothing_doc['_id'] = result.inserted_id
    
    return serialize_clothing(clothing_doc)

def get_clothing_list(query_params):
    col = mongo.get_collection('clothing')
    
    page = int(query_params.get('page', 1))
    limit = int(query_params.get('limit', 12))
    
    if page < 1: page = 1
    if limit < 1 or limit > 100: limit = 12
    
    filter_query = {}
    
    # Filtering
    if 'category' in query_params:
        filter_query['category'] = normalize_category(query_params['category'])
    if 'color' in query_params:
        filter_query['color'] = query_params['color'].strip().lower()
    if 'available' in query_params:
        filter_query['available'] = str(query_params['available']).lower() == 'true'
        
    # Searching
    search = query_params.get('search')
    if search and isinstance(search, str):
        safe_search = re.escape(search.strip())
        filter_query['name'] = {"$regex": safe_search, "$options": "i"}

    # Sorting
    sort_param = query_params.get('sort', 'newest')
    sort_options = {
        'newest': [('created_at', -1)],
        'oldest': [('created_at', 1)],
        'price_asc': [('price', 1)],
        'price_desc': [('price', -1)],
        'name_asc': [('name', 1)],
        'name_desc': [('name', -1)]
    }
    sort_query = sort_options.get(sort_param, sort_options['newest'])

    skip = (page - 1) * limit
    
    cursor = col.find(filter_query).sort(sort_query).skip(skip).limit(limit)
    items = [serialize_clothing(doc) for doc in cursor]
    total = col.count_documents(filter_query)
    pages = (total + limit - 1) // limit

    return {
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages
        }
    }

def get_clothing_by_id(clothing_id):
    try:
        obj_id = ObjectId(clothing_id)
    except InvalidId:
        raise ClothingServiceError("Invalid clothing ID", "INVALID_ID")
        
    col = mongo.get_collection('clothing')
    doc = col.find_one({"_id": obj_id})
    
    if not doc:
        raise ClothingServiceError("Clothing item not found", "CLOTHING_NOT_FOUND")
        
    return serialize_clothing(doc)

def update_clothing(clothing_id, data):
    try:
        obj_id = ObjectId(clothing_id)
    except InvalidId:
        raise ClothingServiceError("Invalid clothing ID", "INVALID_ID")
        
    update_fields = {}
    
    if 'name' in data:
        if not validate_name(data['name']):
            raise ClothingServiceError("Invalid name", "INVALID_NAME")
        update_fields['name'] = data['name'].strip()
        
    if 'category' in data:
        cat = normalize_category(data['category'])
        if cat not in SUPPORTED_CATEGORIES:
            raise ClothingServiceError("Unsupported category", "INVALID_CATEGORY")
        update_fields['category'] = cat
        
    if 'description' in data and isinstance(data['description'], str):
        update_fields['description'] = data['description'].strip()
        
    if 'price' in data:
        if not validate_price(data['price']):
            raise ClothingServiceError("Invalid price", "INVALID_PRICE")
        update_fields['price'] = float(data['price'])
        
    if 'color' in data and isinstance(data['color'], str):
        update_fields['color'] = data['color'].strip().lower()
        
    if 'sizes' in data:
        if not validate_sizes(data['sizes']):
            raise ClothingServiceError("Invalid sizes array", "INVALID_SIZES")
        update_fields['sizes'] = [s.strip().upper() for s in data['sizes']]
        
    if 'available' in data:
        update_fields['available'] = bool(data['available'])
        
    if not update_fields:
        raise ClothingServiceError("No valid fields provided", "NO_UPDATES_PROVIDED")
        
    update_fields['updated_at'] = datetime.datetime.now(datetime.timezone.utc)
    
    col = mongo.get_collection('clothing')
    result = col.update_one({"_id": obj_id}, {"$set": update_fields})
    
    if result.matched_count == 0:
        raise ClothingServiceError("Clothing item not found", "CLOTHING_NOT_FOUND")
        
    return get_clothing_by_id(clothing_id)

def deactivate_clothing(clothing_id):
    try:
        obj_id = ObjectId(clothing_id)
    except InvalidId:
        raise ClothingServiceError("Invalid clothing ID", "INVALID_ID")
        
    col = mongo.get_collection('clothing')
    now = datetime.datetime.now(datetime.timezone.utc)
    
    result = col.update_one(
        {"_id": obj_id},
        {"$set": {"available": False, "updated_at": now}}
    )
    
    if result.matched_count == 0:
        raise ClothingServiceError("Clothing item not found", "CLOTHING_NOT_FOUND")

def associate_image_with_clothing(clothing_id, image_path):
    """Associates an uploaded catalog image with a clothing document."""
    try:
        obj_id = ObjectId(clothing_id)
    except InvalidId:
        from app.services.upload_service import delete_image
        delete_image(image_path)
        raise ClothingServiceError("Invalid clothing ID", "INVALID_ID")

    col = mongo.get_collection('clothing')
    doc = col.find_one({"_id": obj_id})

    if not doc:
        from app.services.upload_service import delete_image
        delete_image(image_path)
        raise ClothingServiceError("Clothing item not found", "CLOTHING_NOT_FOUND")

    old_image = doc.get('image')
    now = datetime.datetime.now(datetime.timezone.utc)

    col.update_one(
        {"_id": obj_id},
        {"$set": {"image": image_path, "updated_at": now}}
    )

    # Safely remove old image if one existed
    if old_image and old_image != image_path:
        from app.services.upload_service import delete_image
        delete_image(old_image)

    return get_clothing_by_id(clothing_id)
