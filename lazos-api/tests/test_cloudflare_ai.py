import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.image_analysis_ai import ImageAnalysisAI
from app.services.image_validation_ai import ImageValidationAI

@pytest.fixture
def mock_settings():
    with patch("app.services.image_analysis_ai.settings") as mock_settings_analysis, \
         patch("app.services.image_validation_ai.settings") as mock_settings_validation:
        mock_settings_analysis.CLOUDFLARE_AI_GATEWAY_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"
        mock_settings_validation.CLOUDFLARE_AI_GATEWAY_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"
        yield mock_settings_analysis

@pytest.mark.asyncio
async def test_image_analysis_ai_authentication_headers(mock_settings):
    """Test that ImageAnalysisAI correctly uses the bearer token and endpoint."""
    account_id = "test_account_id"
    api_token = "test_api_token"
    
    analyzer = ImageAnalysisAI(account_id=account_id, api_token=api_token)
    
    # Assert endpoint is formatted correctly
    assert analyzer.endpoint == f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.2-11b-vision-instruct"
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": {"response": '{"animal_type": "dog"}'}}
        mock_post.return_value = mock_response
        
        await analyzer.analyze_image_for_post(b"test_image_bytes")
        
        # Verify post was called with correct headers and payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == analyzer.endpoint
        assert call_args[1]["headers"]["Authorization"] == f"Bearer {api_token}"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"
        
        # Verify payload structure contains "prompt" and "image" base64 string
        payload = call_args[1]["json"]
        assert "prompt" in payload
        assert "image" in payload
        assert isinstance(payload["image"], str)

@pytest.mark.asyncio
async def test_image_validation_ai_authentication_headers(mock_settings):
    """Test that ImageValidationAI correctly uses the bearer token and endpoint."""
    account_id = "test_account_id"
    api_token = "test_api_token"
    
    validator = ImageValidationAI(account_id=account_id, api_token=api_token)
    
    # Assert endpoint is formatted correctly
    assert validator.endpoint == f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/microsoft/resnet-50"
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": [{"label": "dog", "score": 0.99}]}
        mock_post.return_value = mock_response
        
        await validator.validate_image(b"test_image_bytes")
        
        # Verify post was called with correct headers
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == validator.endpoint
        assert call_args[1]["headers"]["Authorization"] == f"Bearer {api_token}"
        assert call_args[1]["headers"]["Content-Type"] == "application/octet-stream"
        assert call_args[1]["content"] == b"test_image_bytes"
