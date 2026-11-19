"""
Tests for critical API endpoints: posts, alerts, and search
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from datetime import date, datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db as db_get_db
from app.api.deps import get_db as api_get_db
from app.models.post import Post, SexEnum, SizeEnum, AnimalEnum
from app.models.alert import Alert

# We override the dependencies using fastapi dependency_overrides
client = TestClient(app)

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


def test_list_posts_endpoint(mock_db):
    """Test getting public lists of active posts"""
    # Create mock Post
    mock_post = Post(
        id=uuid4(),
        image_url="http://example.com/image.jpg",
        thumbnail_url="http://example.com/thumb.jpg",
        sex=SexEnum.male,
        size=SizeEnum.medium,
        animal_type=AnimalEnum.dog,
        description="Perro perdido rescatado",
        location_name="Palermo, Buenos Aires",
        sighting_date=date.today(),
        created_at=datetime.utcnow(),
        is_active=True,
        pending_approval=False
    )
    
    # Filter distinct query returns a list of location strings, and posts query returns list of posts
    mock_db.execute.return_value.scalars.return_value.all.side_effect = [
        [mock_post],                  # First call (posts query)
        ["Palermo, Buenos Aires"],    # Second call (location distinct query)
    ]
    mock_db.query.return_value.filter.return_value.count.return_value = 1
    
    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    
    json_data = response.json()
    assert "data" in json_data
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["description"] == "Perro perdido rescatado"
    assert json_data["data"][0]["latitude"] == -34.6037
    assert json_data["data"][0]["longitude"] == -58.3816


def test_get_alerts_list_endpoint(mock_db):
    """Test getting list of warning alerts"""
    # Create mock Alert
    mock_alert = Alert(
        id=uuid4(),
        description="Perro suelto corriendo rápido por la avenida",
        animal_type=AnimalEnum.dog,
        direction="hacia el norte",
        location_name="Belgrano, CABA",
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    # Mock db query return
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_alert]
    
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    
    json_data = response.json()
    assert "data" in json_data
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["direction"] == "hacia el norte"


@pytest.mark.asyncio
@patch("app.api.routes.alerts.get_text_validation_ai")
async def test_create_alert_endpoint(mock_text_validation, mock_db):
    """Test creating an alert successfully"""
    # Mock the text validation AI response to return safe as an AsyncMock
    mock_validator = MagicMock()
    mock_validator.validate_sighting_text = AsyncMock(return_value={"is_valid": True, "reason": None})
    mock_text_validation.return_value = mock_validator
    
    # Setup returned alert after creation
    mock_alert_id = uuid4()
    
    # Prepare session mock setup to mock creation and DB-assigned fields
    def mock_refresh(obj):
        setattr(obj, "id", mock_alert_id)
        setattr(obj, "location", "POINT(-64.1887 -31.4165)")
        setattr(obj, "created_at", datetime.utcnow())
        setattr(obj, "is_active", True)
        
    mock_db.refresh = mock_refresh
    mock_db.scalar.return_value = "POINT(-64.1887 -31.4165)"
    
    alert_payload = {
        "description": "Gatito herido en la calle",
        "animal_type": "cat",
        "latitude": -31.4165,
        "longitude": -64.1887,
        "direction": "sin rumbo",
        "location_name": "Cordoba"
    }
    
    response = client.post("/api/v1/alerts", json=alert_payload)
    assert response.status_code == 201
    
    json_data = response.json()
    assert json_data["description"] == "Gatito herido en la calle"
    assert json_data["latitude"] == -31.4165
    assert json_data["longitude"] == -64.1887


def test_unified_search_endpoint(mock_db):
    """Test unified search filters can query both resources"""
    mock_post = Post(
        id=uuid4(),
        image_url="http://example.com/image.jpg",
        thumbnail_url="http://example.com/thumb.jpg",
        sex=SexEnum.female,
        size=SizeEnum.small,
        animal_type=AnimalEnum.cat,
        description="Gata blanca perdida",
        location_name="Rosario",
        sighting_date=date.today(),
        created_at=datetime.utcnow(),
        is_active=True,
        pending_approval=False
    )
    
    mock_alert = Alert(
        id=uuid4(),
        description="Gatito blanco suelto",
        animal_type=AnimalEnum.cat,
        direction="hacia la esquina",
        location_name="Rosario",
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    # Simulate DB query return for posts and alerts separately
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [mock_post],  # Returned for post query
        [mock_alert]  # Returned for alert query
    ]
    
    response = client.get("/api/v1/search?q=blanco&type=all")
    assert response.status_code == 200
    
    json_data = response.json()
    assert "posts" in json_data
    assert "alerts" in json_data
    assert len(json_data["posts"]) == 1
    assert len(json_data["alerts"]) == 1
    assert json_data["posts"][0]["description"] == "Gata blanca perdida"
    assert json_data["alerts"][0]["description"] == "Gatito blanco suelto"


@pytest.mark.asyncio
async def test_analyze_image_endpoint(mock_db):
    """Test analyzing an image for post auto-completion"""
    mock_analyzer = MagicMock()
    mock_analyzer.analyze_image_for_post = AsyncMock(return_value={
        "extracted_text": "PERRO PERDIDO.",
        "image_interpretation": "Se busca perro mestizo negro, con collar rojo. Visto cerca de la plaza.",
        "animal_type": "dog",
        "sex": "male",
        "size": "medium",
        "location_name": "Plaza Principal",
        "contact_method": "12345678",
        "sighting_date": "2023-10-01"
    })
    
    from app.api.routes.posts import get_image_analysis_ai
    app.dependency_overrides[get_image_analysis_ai] = lambda: mock_analyzer
    
    try:
        # We also need to mock ImageService.validate_image and process_for_ai so it doesn't fail on dummy data
        with patch("app.api.routes.posts.ImageService.validate_image") as mock_validate, \
             patch("app.api.routes.posts.ImageService.process_for_ai") as mock_process_for_ai:
            mock_validate.return_value = None
            mock_process_for_ai.return_value = b"dummy processed bytes"
            
            # Create a dummy image file
            file_content = b"dummy image content"
            files = {
                "image": ("test.jpg", file_content, "image/jpeg")
            }
            
            response = client.post("/api/v1/posts/analyze-image", files=files)
            
            assert response.status_code == 200
            json_data = response.json()
            assert json_data["animal_type"] == "dog"
            assert json_data["sex"] == "male"
            assert json_data["size"] == "medium"
            assert json_data["location_name"] == "Plaza Principal"
            assert json_data["contact_method"] == "12345678"
            assert json_data["extracted_text"] == "PERRO PERDIDO."
            assert json_data["image_interpretation"].startswith("Se busca perro")
    finally:
        app.dependency_overrides.pop(get_image_analysis_ai, None)
