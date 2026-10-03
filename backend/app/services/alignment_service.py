"""
app/services/alignment_service.py

Service layer for garment alignment.
Coordinates database lookups, security rules, and the AI alignment module.
"""

import os
from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.extensions import mongo
from app.ai.pose_detection import detect_pose, PoseDetectionError
from app.ai.body_analysis import analyse_body, BodyAnalysisError
from app.ai.garment_processing import process_garment, GarmentProcessingError
from app.ai.garment_alignment import align_garment, GarmentAlignmentError


class AlignmentServiceError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


def perform_garment_alignment(person_image_id: str, clothing_id_str: str, current_user: dict) -> dict:
    """
    Coordinates the 2D alignment of a garment onto a person image.
    
    person_image_id : The relative path to the preprocessed person image.
    clothing_id_str : The MongoDB ID of the catalog or user custom clothing.
    """
    # 1. Verify person image path is safe and belongs to processed users
    if not person_image_id or not person_image_id.startswith("processed/users/"):
        raise AlignmentServiceError("Invalid person image reference. Must be a processed user image.", "INVALID_PERSON_REFERENCE")
        
    upload_root = current_app.config['UPLOAD_FOLDER']
    person_abs_path = os.path.join(upload_root, os.path.normpath(person_image_id))
    
    if not os.path.abspath(person_abs_path).startswith(os.path.abspath(upload_root)):
        raise AlignmentServiceError("Path traversal detected", "INVALID_PATH")
        
    if not os.path.isfile(person_abs_path):
        raise AlignmentServiceError("Person image not found", "PERSON_NOT_FOUND")

    # 2. Resolve clothing item
    try:
        clothing_id = ObjectId(clothing_id_str)
    except InvalidId:
        raise AlignmentServiceError("Invalid clothing ID format", "INVALID_ID")
        
    db = mongo.get_db()
    
    # Try catalog first
    clothing_record = db.clothing.find_one({"_id": clothing_id})
    if clothing_record:
        source_type = "catalog"
    else:
        # Try user custom clothing
        clothing_record = db.user_clothing.find_one({"_id": clothing_id})
        if not clothing_record:
            raise AlignmentServiceError("Clothing item not found", "NOT_FOUND")
            
        if str(clothing_record.get("user_id")) != current_user["id"]:
            raise AlignmentServiceError("You do not have permission to use this custom clothing item", "FORBIDDEN")
        source_type = "user_custom"
        
    original_clothing_path = clothing_record.get("image")
    category = clothing_record.get("category", "unknown")
    
    if not original_clothing_path:
        raise AlignmentServiceError("Clothing item is missing an image", "MISSING_IMAGE")

    # 3. Retrieve Pose & Body Analysis
    try:
        pose_result = detect_pose(person_abs_path)
        if not pose_result.get("person_detected"):
            raise AlignmentServiceError("No person detected in the image for alignment", "NO_PERSON")
            
        # analyse_body calculates body geometry
        body_analysis = analyse_body(pose_result)
        pose_result["body_analysis"] = body_analysis
        
    except (PoseDetectionError, BodyAnalysisError) as e:
        # Map specific exceptions
        raise AlignmentServiceError(f"Unable to align garment because required body landmarks were not detected. ({e.message})", "INSUFFICIENT_POSE_DATA")
    except Exception as e:
        current_app.logger.error(f"Pose extraction failed during alignment: {e}")
        raise AlignmentServiceError("Failed to extract body landmarks", "INTERNAL_ERROR")

    # 4. Retrieve Garment Geometry (processes the garment on-the-fly or uses cached logic)
    try:
        garment_info = process_garment(clothing_id_str, original_clothing_path, source_type, category)
    except GarmentProcessingError as e:
        raise AlignmentServiceError(e.message, e.code)
        
    garment_processed_path = os.path.join(upload_root, os.path.normpath(garment_info["processed_image"]))
    garment_geometry = garment_info["geometry"]

    # 5. Run Alignment
    try:
        alignment_result = align_garment(
            person_image_path=person_abs_path,
            pose_result=pose_result,
            garment_image_path=garment_processed_path,
            garment_geometry=garment_geometry,
            category=category
        )
    except GarmentAlignmentError as e:
        raise AlignmentServiceError(e.message, e.code)

    return alignment_result
