import pytest
import uuid
from unittest.mock import AsyncMock
from backend.main import app
from backend.app.dependencies.adapters import get_image_adapter


@pytest.fixture
def mock_image_adapter():
    mock = AsyncMock()
    app.dependency_overrides[get_image_adapter] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_image_adapter, None)


@pytest.mark.asyncio
async def test_get_latest_images(async_client, mock_image_adapter):
    pet_id = uuid.uuid4()
    # Now it returns base64 strings instead of paths
    mock_image_adapter.get_latest_images.return_value = [
        "base64_encoded_string_1",
        "base64_encoded_string_2",
    ]

    response = await async_client.get(f"/images/{pet_id}/latest?limit=5")

    assert response.status_code == 200
    assert response.json() == ["base64_encoded_string_1", "base64_encoded_string_2"]

    mock_image_adapter.get_latest_images.assert_called_once_with(pet_id, 5)


@pytest.mark.asyncio
async def test_get_latest_images_error(async_client, mock_image_adapter):
    pet_id = uuid.uuid4()
    mock_image_adapter.get_latest_images.side_effect = Exception("DB Error")

    response = await async_client.get(f"/images/{pet_id}/latest")

    assert response.status_code == 500
    assert "Failed to get latest images" in response.json()["detail"]
