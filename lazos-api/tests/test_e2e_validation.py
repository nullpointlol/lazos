"""
E2E integration tests for the full image validation flow.
These tests do NOT mock the Cloudflare AI services, ensuring the actual endpoints work.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db as db_get_db
from app.api.deps import get_db as api_get_db

client = TestClient(app)

import os

# Imágenes reales para el e2e (llama a Cloudflare de verdad): no se versionan.
# Poné img_test.jpg e img_test_with_text.jpg en LAZOS_IMG_TEST_DIR (por defecto, tests/fixtures).
IMG_TEST_DIR = Path(os.environ.get("LAZOS_IMG_TEST_DIR", Path(__file__).resolve().parent / "fixtures"))
pytestmark = pytest.mark.skipif(
    not (IMG_TEST_DIR / "img_test.jpg").exists(),
    reason="faltan las imágenes de prueba en LAZOS_IMG_TEST_DIR",
)

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.scalar.return_value = "POINT(-58.3816 -34.6037)"
    db.execute.return_value.scalar_one.return_value = 1
    
    def override_get_db():
        yield db
        
    app.dependency_overrides[db_get_db] = override_get_db
    app.dependency_overrides[api_get_db] = override_get_db
    
    yield db
    
    app.dependency_overrides.pop(db_get_db, None)
    app.dependency_overrides.pop(api_get_db, None)


@pytest.mark.asyncio
@patch("app.api.routes.posts.get_storage_service")
async def test_e2e_create_post_with_image(mock_storage_service, mock_db):
    """Test full validation flow with the standard img_test.jpg image."""
    img_path = IMG_TEST_DIR / "img_test.jpg"
    assert img_path.exists(), f"Test image not found at: {img_path}"

    mock_storage = MagicMock()
    mock_storage.upload_images.return_value = [
        ("http://example.com/uploaded_img.jpg", "http://example.com/uploaded_thumb.jpg")
    ]
    mock_storage_service.return_value = mock_storage

    mock_post_id = uuid4()
    def mock_refresh(obj):
        setattr(obj, "id", mock_post_id)
        setattr(obj, "location", "POINT(-58.3816 -34.6037)")
        setattr(obj, "created_at", datetime.utcnow())
        setattr(obj, "is_active", True)
        
    mock_db.refresh = mock_refresh
    mock_db.scalar.return_value = "POINT(-58.3816 -34.6037)"

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

        # This will call the REAL get_hybrid_validator and get_text_validation_ai
        response = client.post("/api/v1/posts", files=files, data=form_data)

    assert response.status_code == 201, f"Response failed: {response.text}"
    json_data = response.json()
    assert json_data["image_url"] == "http://example.com/uploaded_img.jpg"


@pytest.mark.asyncio
@patch("app.api.routes.posts.get_storage_service")
async def test_e2e_create_post_with_text_image(mock_storage_service, mock_db):
    """Test full validation flow with the text-heavy img_test_with_text.jpg image."""
    img_path = IMG_TEST_DIR / "img_test_with_text.jpg"
    assert img_path.exists(), f"Test image not found at: {img_path}"

    mock_storage = MagicMock()
    mock_storage.upload_images.return_value = [
        ("http://example.com/uploaded_img_text.jpg", "http://example.com/uploaded_thumb_text.jpg")
    ]
    mock_storage_service.return_value = mock_storage

    mock_post_id = uuid4()
    def mock_refresh(obj):
        setattr(obj, "id", mock_post_id)
        setattr(obj, "location", "POINT(-58.3816 -34.6037)")
        setattr(obj, "created_at", datetime.utcnow())
        setattr(obj, "is_active", True)
        
    mock_db.refresh = mock_refresh
    mock_db.scalar.return_value = "POINT(-58.3816 -34.6037)"

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


@pytest.mark.asyncio
async def test_e2e_analyze_image_with_text():
    """Test the analyze-image endpoint with real Cloudflare AI using an image with text."""
    img_path = IMG_TEST_DIR / "img_test_with_text.jpg"
    assert img_path.exists(), f"Test image not found at: {img_path}"

    with open(img_path, "rb") as f:
        files = {
            "image": ("img_test_with_text.jpg", f, "image/jpeg")
        }
        response = client.post("/api/v1/posts/analyze-image", files=files)

    assert response.status_code == 200, f"Response failed: {response.text}"
    json_data = response.json()
    
    # Check that error is None (no exception was thrown)
    assert json_data.get("error") is None, f"An unexpected error occurred during image analysis: {json_data.get('error')}"
    
    # Check that both parts are present in the response
    assert "extracted_text" in json_data
    assert "image_interpretation" in json_data
    # animal_type should be detected
    assert "animal_type" in json_data
    # There should be some extracted text
    assert json_data["extracted_text"] is not None


@pytest.mark.asyncio
async def test_e2e_analyze_image_no_text():
    """Test the analyze-image endpoint with real Cloudflare AI using an image with no text."""
    img_path = IMG_TEST_DIR / "img_test.jpg"
    assert img_path.exists(), f"Test image not found at: {img_path}"

    with open(img_path, "rb") as f:
        files = {
            "image": ("img_test.jpg", f, "image/jpeg")
        }
        response = client.post("/api/v1/posts/analyze-image", files=files)

    assert response.status_code == 200, f"Response failed: {response.text}"
    json_data = response.json()
    
    # Check that error is None (no exception was thrown)
    assert json_data.get("error") is None, f"An unexpected error occurred during image analysis: {json_data.get('error')}"
    
    # Check that both parts are present in the response
    assert "extracted_text" in json_data or json_data["extracted_text"] == ""
    assert "image_interpretation" in json_data
    # animal_type should be detected
    assert "animal_type" in json_data


@pytest.mark.asyncio
@patch("app.services.image_analysis_ai.httpx.AsyncClient.post")
async def test_e2e_analyze_image_giant_payload_crash(mock_post):
    """Test that a giant payload crash inside the AI service returns the raw exception instead of unexpected_error."""
    # Simulate an exception raised by the HTTP client (e.g., Payload Too Large, memory error or native exception)
    mock_post.side_effect = Exception("Giant Base64 payload crash (simulated)")

    img_path = IMG_TEST_DIR / "img_test.jpg"
    with open(img_path, "rb") as f:
        files = {
            "image": ("img_test.jpg", f, "image/jpeg")
        }
        response = client.post("/api/v1/posts/analyze-image", files=files)

    assert response.status_code == 200, f"Response failed: {response.text}"
    json_data = response.json()
    
    # Assert that the error is the raw exception string and NOT the unexpected_error mask
    assert json_data["error"] == "Giant Base64 payload crash (simulated)"
    assert json_data["error"] != "unexpected_error"
