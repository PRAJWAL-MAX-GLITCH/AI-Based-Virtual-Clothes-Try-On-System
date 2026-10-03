import pytest
import os
from PIL import Image
from app.ai.virtual_tryon import composite_tryon, VirtualTryonError

def test_composite_tryon_missing_person(tmp_path, app):
    with app.app_context():
        with pytest.raises(VirtualTryonError) as exc:
            composite_tryon(str(tmp_path / "nonexistent.png"), "garment.png", "shirt", {})
        assert exc.value.code == "PERSON_IMAGE_NOT_FOUND"

def test_composite_tryon_missing_garment(tmp_path, app):
    person_img = tmp_path / "person.png"
    person_img.touch()
    with app.app_context():
        with pytest.raises(VirtualTryonError) as exc:
            composite_tryon(str(person_img), str(tmp_path / "nonexistent.png"), "shirt", {})
        assert exc.value.code == "ALIGNED_GARMENT_NOT_FOUND"

def test_composite_tryon_success(tmp_path, app):
    # Setup test images
    person_img_path = tmp_path / "person.png"
    # Create an RGB image (person)
    Image.new("RGB", (768, 1024), "blue").save(person_img_path)
    
    garment_img_path = tmp_path / "garment.png"
    # Create an RGBA image (garment layer, same size)
    garment = Image.new("RGBA", (768, 1024), (0, 0, 0, 0))
    # Draw something
    from PIL import ImageDraw
    draw = ImageDraw.Draw(garment)
    draw.rectangle([300, 300, 468, 600], fill=(255, 0, 0, 255)) # Red shirt in the middle
    garment.save(garment_img_path)

    with app.app_context():
        result = composite_tryon(str(person_img_path), str(garment_img_path), "shirt", {"scale": 1.0})
    
    assert result["success"] is True
    assert result["category"] == "shirt"
    assert result["image_size"]["width"] == 768
    assert result["image_size"]["height"] == 1024
    
    # Check file exists and can be opened
    upload_root = app.config['UPLOAD_FOLDER']
    output_path = os.path.join(upload_root, result["result_image"])
    assert os.path.exists(output_path)
    
    out_img = Image.open(output_path)
    assert out_img.size == (768, 1024)
    # Check if composited correctly (middle pixel should be red)
    out_img = out_img.convert("RGB")
    assert out_img.getpixel((384, 450)) == (255, 0, 0)
    # Background pixel should remain blue
    assert out_img.getpixel((10, 10)) == (0, 0, 255)
