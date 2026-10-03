import pytest
import os
from app.ai.garment_alignment import align_garment, GarmentAlignmentError, GARMENT_ALIGNMENT_CONFIG

def test_align_garment_missing_person(tmp_path):
    with pytest.raises(GarmentAlignmentError) as exc:
        align_garment(str(tmp_path / "nonexistent.png"), {}, "garment.png", {}, "shirt")
    assert exc.value.code == "PERSON_IMAGE_NOT_FOUND"

def test_align_garment_missing_garment(tmp_path):
    person_img = tmp_path / "person.png"
    person_img.touch()
    with pytest.raises(GarmentAlignmentError) as exc:
        align_garment(str(person_img), {}, str(tmp_path / "nonexistent.png"), {}, "shirt")
    assert exc.value.code == "GARMENT_IMAGE_NOT_FOUND"

def test_align_garment_missing_pose_data(tmp_path):
    person_img = tmp_path / "person.png"
    person_img.touch()
    garment_img = tmp_path / "garment.png"
    garment_img.touch()
    
    with pytest.raises(GarmentAlignmentError) as exc:
        align_garment(str(person_img), {"person_detected": False}, str(garment_img), {}, "shirt")
    assert exc.value.code == "INSUFFICIENT_POSE_DATA"

def test_align_garment_success(tmp_path, app):
    # Setup test images
    from PIL import Image
    person_img_path = tmp_path / "person.png"
    Image.new("RGB", (768, 1024), "white").save(person_img_path)
    
    garment_img_path = tmp_path / "garment.png"
    # Create a small garment image
    Image.new("RGBA", (200, 300), (255, 0, 0, 255)).save(garment_img_path)

    pose_result = {
        "person_detected": True,
        "image_width": 768,
        "image_height": 1024,
        "body_analysis": {
            "shoulder_width": 0.3,  # 0.3 * 768 = 230.4 px
            "shoulder_center": {"x": 0.5, "y": 0.25}, # 384, 256 px
            "shoulder_angle": 10.0
        }
    }
    
    garment_geometry = {
        "garment_width": 180,
        "center": {"x": 100, "y": 150}
    }

    with app.app_context():
        result = align_garment(str(person_img_path), pose_result, str(garment_img_path), garment_geometry, "shirt")
    
    assert result["success"] is True
    assert result["category"] == "shirt"
    
    # Check transformation metadata
    trans = result["transformation"]
    expected_shoulder_px = 768 * 0.3
    # Config for shirt is 1.4 scale multiplier
    mult = GARMENT_ALIGNMENT_CONFIG["shirt"]["scale_multiplier"]
    expected_scale = (expected_shoulder_px / 180) * mult
    
    assert abs(trans["scale"] - expected_scale) < 0.01
    assert trans["rotation_degrees"] == 10.0
    
    # Check file exists
    import os
    upload_root = app.config['UPLOAD_FOLDER']
    assert os.path.exists(os.path.join(upload_root, result["aligned_garment"]))
