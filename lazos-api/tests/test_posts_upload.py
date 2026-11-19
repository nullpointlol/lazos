"""
API integration tests for pet sighting post creation with image uploads.
Validates that both `img_test.jpg` and `img_test_with_text.jpg` are processed
successfully and do not trigger UnicodeEncodeError or invalid JSON responses on Windows.
"""
import os
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from datetime import date, datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db as db_get_db
from app.api.deps import get_db as api_get_db
from app.models.post import Post, SexEnum, SizeEnum, AnimalEnum

# Create test client
client = TestClient(app)

# Synthetic test images (no real photos)
IMG_TEST_DIR = Path(__file__).resolve().parent / "fixtures"

@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mock db.scalar to return standard POINT string for PostGIS ST_AsText format
    db.scalar.return_value = "POINT(-58.3816 -34.6037)"
    
    # Mock count return scalar
    db.execute.return_value.scalar_one.return_value = 1
    
    # Setup dependency override
    def override_get_db():
        yield db
        
    app.dependency_overrides[db_get_db] = override_get_db
    app.dependency_overrides[api_get_db] = override_get_db
    
    yield db
    
    # Clean up overrides
    app.dependency_overrides.pop(db_get_db, None)
    app.dependency_overrides.pop(api_get_db, None)


@pytest.mark.asyncio
@patch("app.api.routes.posts.get_hybrid_validator")
@patch("app.api.routes.posts.get_storage_service")
@patch("app.api.routes.posts.get_text_validation_ai")
async def test_create_post_with_image(mock_text_validation, mock_storage_service, mock_hybrid_validator, mock_db):
    """Test creating a post with the standard img_test.jpg image."""
    img_path = IMG_TEST_DIR / "img_test.jpg"
    assert img_path.exists(), f"Test image not found at: {img_path}"

    # Setup hybrid validator mock (Fase 2)
    mock_val = MagicMock()
    mock_val.validate_all = AsyncMock(return_value={
        "is_valid": True,
        "service": "python_nsfw",
        "reason": None
    })
    mock_hybrid_validator.return_value = mock_val

    # Setup storage service mock
    mock_storage = MagicMock()
    mock_storage.upload_images.return_value = [
        ("http://example.com/uploaded_img.jpg", "http://example.com/uploaded_thumb.jpg")
    ]
    mock_storage_service.return_value = mock_storage

    # Setup text validator mock
    mock_text_val = MagicMock()
    mock_text_val.validate_sighting_text = AsyncMock(return_value={
        "is_valid": True,
        "reason": None
    })
    mock_text_validation.return_value = mock_text_val

    # Mock database methods
    mock_post_id = uuid4()
    def mock_refresh(obj):
        setattr(obj, "id", mock_post_id)
        setattr(obj, "location", "POINT(-58.3816 -34.6037)")
        setattr(obj, "created_at", datetime.utcnow())
        setattr(obj, "is_active", True)
        
    mock_db.refresh = mock_refresh
    mock_db.scalar.return_value = "POINT(-58.3816 -34.6037)"

    # Submit request with the real image file
    with open(img_path, "rb") as f:
        files = {
            "images": ("img_test.jpg", f, "image/jpeg")
        }
        form_data = {
            "latitude": -34.6037,
            "longitude": -58.3816,
            "size": "medium",
            "animal_type": "dog",
            "sex": "male",
            "sighting_date": "2026-07-10",
            "description": "Perro perdido en la calle corriendo muy feliz",
            "location_name": "Palermo, Buenos Aires"
        }

        response = client.post("/api/v1/posts", files=files, data=form_data)

    assert response.status_code == 201, f"Response failed: {response.text}"
    json_data = response.json()
    assert json_data["image_url"] == "http://example.com/uploaded_img.jpg"
    assert json_data["thumbnail_url"] == "http://example.com/uploaded_thumb.jpg"
    assert json_data["animal_type"] == "dog"
    assert json_data["sex"] == "male"
    assert json_data["latitude"] == -34.6037
    assert json_data["longitude"] == -58.3816


@pytest.mark.asyncio
@patch("app.api.routes.posts.get_hybrid_validator")
@patch("app.api.routes.posts.get_storage_service")
@patch("app.api.routes.posts.get_text_validation_ai")
async def test_create_post_with_text_image(mock_text_validation, mock_storage_service, mock_hybrid_validator, mock_db):
    """Test creating a post with the text-heavy img_test_with_text.jpg image."""
    img_path = IMG_TEST_DIR / "img_test_with_text.jpg"
    assert img_path.exists(), f"Test image not found at: {img_path}"

    # Setup hybrid validator mock (Fase 2)
    mock_val = MagicMock()
    mock_val.validate_all = AsyncMock(return_value={
        "is_valid": True,
        "service": "python_nsfw",
        "reason": None
    })
    mock_hybrid_validator.return_value = mock_val

    # Setup storage service mock
    mock_storage = MagicMock()
    mock_storage.upload_images.return_value = [
        ("http://example.com/uploaded_img_text.jpg", "http://example.com/uploaded_thumb_text.jpg")
    ]
    mock_storage_service.return_value = mock_storage

    # Setup text validator mock
    mock_text_val = MagicMock()
    mock_text_val.validate_sighting_text = AsyncMock(return_value={
        "is_valid": True,
        "reason": None
    })
    mock_text_validation.return_value = mock_text_val

    # Mock database methods
    mock_post_id = uuid4()
    def mock_refresh(obj):
        setattr(obj, "id", mock_post_id)
        setattr(obj, "location", "POINT(-58.3816 -34.6037)")
        setattr(obj, "created_at", datetime.utcnow())
        setattr(obj, "is_active", True)
        
    mock_db.refresh = mock_refresh
    mock_db.scalar.return_value = "POINT(-58.3816 -34.6037)"

    # Submit request with the real image file
    with open(img_path, "rb") as f:
        files = {
            "images": ("img_test_with_text.jpg", f, "image/jpeg")
        }
        form_data = {
            "latitude": -34.6037,
            "longitude": -58.3816,
            "size": "medium",
            "animal_type": "dog",
            "sex": "male",
            "sighting_date": "2026-07-10",
            "description": "Perro con cartel de busqueda",
            "location_name": "Palermo, Buenos Aires"
        }

        response = client.post("/api/v1/posts", files=files, data=form_data)

    assert response.status_code == 201, f"Response failed: {response.text}"
    json_data = response.json()
    assert json_data["image_url"] == "http://example.com/uploaded_img_text.jpg"
    assert json_data["thumbnail_url"] == "http://example.com/uploaded_thumb_text.jpg"
    assert json_data["animal_type"] == "dog"
    assert json_data["sex"] == "male"
    assert json_data["latitude"] == -34.6037
    assert json_data["longitude"] == -58.3816
