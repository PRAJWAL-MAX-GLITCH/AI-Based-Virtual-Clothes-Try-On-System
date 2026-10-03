"""
app/services/pipeline_service.py

Orchestrates the complete 2D Virtual Try-On pipeline.
Coordinates the AI modules without duplicating their internal logic.
"""

import os
from datetime import datetime, timezone
from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.extensions import mongo

from app.ai.pose_detection import detect_pose, PoseDetectionError
from app.ai.body_analysis import analyse_body, BodyAnalysisError
from app.ai.garment_processing import process_garment, GarmentProcessingError
from app.ai.garment_alignment import align_garment, GarmentAlignmentError
from app.ai.virtual_tryon import composite_tryon, VirtualTryonError


class PipelineServiceError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


class TryOnPipeline:
    def __init__(self, current_user):
        self.current_user = current_user
        self.upload_root = current_app.config['UPLOAD_FOLDER']
        self.db = mongo.get_db()

    def run(self, person_image_id: str, clothing_id_str: str) -> dict:
        """
        Executes the complete Try-On pipeline.
        """
        try:
            current_app.logger.info(f"Pipeline started for user {self.current_user['id']}")
            
            # STEP 1 & 2 & 3: Validate Person Image
            person_abs_path = self._validate_person_image(person_image_id)
            
            # STEP 4 & 5 & 6: Validate Clothing
            clothing_record, source_type = self._validate_clothing(clothing_id_str)
            original_clothing_path = clothing_record.get("image")
            category = clothing_record.get("category", "unknown")
            
            # STEP 7 & 8: Preprocessing Person Image (Already done, we use the processed image)
            # STEP 9: Pose Detection
            current_app.logger.info("Running pose detection...")
            try:
                pose_result = detect_pose(person_abs_path)
                if not pose_result.get("person_detected"):
                    raise PipelineServiceError("No person detected in the image", "INSUFFICIENT_POSE_DATA")
            except PoseDetectionError as e:
                raise PipelineServiceError(e.message, "POSE_DETECTION_FAILED")
                
            # STEP 10: Body Analysis
            current_app.logger.info("Running body analysis...")
            try:
                body_analysis = analyse_body(pose_result)
                pose_result["body_analysis"] = body_analysis
            except BodyAnalysisError as e:
                raise PipelineServiceError(e.message, "BODY_ANALYSIS_FAILED")
                
            # STEP 11 & 12 & 13: Garment Processing
            current_app.logger.info("Running garment processing...")
            try:
                garment_info = process_garment(clothing_id_str, original_clothing_path, source_type, category)
            except GarmentProcessingError as e:
                raise PipelineServiceError(e.message, "GARMENT_PROCESSING_FAILED")
                
            garment_processed_path = os.path.join(self.upload_root, os.path.normpath(garment_info["processed_image"]))
            garment_geometry = garment_info["geometry"]
            
            # STEP 14: Garment Alignment
            current_app.logger.info("Running garment alignment...")
            try:
                alignment_result = align_garment(
                    person_image_path=person_abs_path,
                    pose_result=pose_result,
                    garment_image_path=garment_processed_path,
                    garment_geometry=garment_geometry,
                    category=category
                )
            except GarmentAlignmentError as e:
                raise PipelineServiceError(e.message, "GARMENT_ALIGNMENT_FAILED")
                
            aligned_garment_abs_path = os.path.join(self.upload_root, os.path.normpath(alignment_result["aligned_garment"]))
            transformation = alignment_result.get("transformation", {})
            
            # STEP 15: Virtual Try-On Compositing
            current_app.logger.info("Running virtual try-on compositing...")
            try:
                tryon_output = composite_tryon(person_abs_path, aligned_garment_abs_path, category, transformation)
            except VirtualTryonError as e:
                raise PipelineServiceError(e.message, "COMPOSITING_FAILED")
                
            # STEP 16: Result Validation is handled inside composite_tryon
            
            # STEP 17: Save Result
            current_app.logger.info("Saving try-on result and history...")
            
            clothing_name = clothing_record.get("name") if source_type == "catalog" else "Custom Clothing"
            
            history_record = {
                "user_id": ObjectId(self.current_user["id"]),
                "person_image_id": person_image_id,
                "clothing_id": ObjectId(clothing_id_str),
                "clothing_source": source_type,
                "clothing_name": clothing_name,
                "clothing_category": category,
                "result_image": tryon_output["result_image"],
                "status": "completed",
                "transformation": transformation,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            history_id = self.db.tryon_history.insert_one(history_record).inserted_id
            
            current_app.logger.info(f"Pipeline completed. History ID: {history_id}")
            
            try:
                if os.path.exists(aligned_garment_abs_path):
                    os.remove(aligned_garment_abs_path)
            except Exception as e:
                current_app.logger.warning(f"Failed to cleanup intermediate aligned garment: {e}")
            
            # STEP 18: Return Result
            return {
                "success": True,
                "message": "Virtual try-on completed successfully",
                "data": {
                    "result_id": str(history_id),
                    "result_image": tryon_output["result_image"],
                    "clothing": {
                        "id": clothing_id_str,
                        "category": category,
                        "source_type": source_type
                    },
                    "image": tryon_output["image_size"]
                }
            }
            
        except PipelineServiceError as e:
            current_app.logger.error(f"Pipeline failed: {e.message}")
            raise e
        except Exception as e:
            current_app.logger.error(f"Unexpected pipeline error: {e}")
            raise PipelineServiceError("An unexpected error occurred during processing", "TRYON_PIPELINE_FAILED")

    def _validate_person_image(self, person_image_id: str) -> str:
        if not person_image_id or not person_image_id.startswith("processed/users/"):
            raise PipelineServiceError("Invalid person image reference.", "INVALID_PERSON_IMAGE")
            
        person_abs_path = os.path.join(self.upload_root, os.path.normpath(person_image_id))
        
        if not os.path.abspath(person_abs_path).startswith(os.path.abspath(self.upload_root)):
            raise PipelineServiceError("Path traversal detected", "INVALID_PERSON_IMAGE")
            
        if not os.path.isfile(person_abs_path):
            raise PipelineServiceError("Person image not found", "PERSON_IMAGE_NOT_FOUND")
            
        return person_abs_path

    def _validate_clothing(self, clothing_id_str: str) -> tuple[dict, str]:
        if not clothing_id_str:
            raise PipelineServiceError("Missing clothing ID", "INVALID_CLOTHING")
            
        try:
            clothing_id = ObjectId(clothing_id_str)
        except InvalidId:
            raise PipelineServiceError("Invalid clothing ID format", "INVALID_CLOTHING")
            
        # Catalog check
        clothing_record = self.db.clothing.find_one({"_id": clothing_id})
        if clothing_record:
            if not clothing_record.get("available", True):
                raise PipelineServiceError("Catalog clothing is currently unavailable", "CLOTHING_UNAVAILABLE")
            return clothing_record, "catalog"
            
        # Custom clothing check
        clothing_record = self.db.user_clothing.find_one({"_id": clothing_id})
        if not clothing_record:
            raise PipelineServiceError("Clothing item not found", "CLOTHING_NOT_FOUND")
            
        if str(clothing_record.get("user_id")) != self.current_user["id"]:
            raise PipelineServiceError("You do not have permission to use this custom clothing item", "UNAUTHORIZED_CLOTHING")
            
        return clothing_record, "user_custom"
