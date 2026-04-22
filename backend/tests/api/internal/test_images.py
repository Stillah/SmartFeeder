import pytest
import uuid
from unittest.mock import AsyncMock
from backend.main import app
from backend.app.dependencies.adapters import get_image_adapter
from backend.infrastructure.exceptions.image import ClassificationError

@pytest.fixture
def mock_image_adapter():
    mock = AsyncMock()
    app.dependency_overrides[get_image_adapter] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_image_adapter, None)

@pytest.mark.asyncio
async def test_send_image(async_client, mock_image_adapter):
    user_id = uuid.uuid4()
    image_id = uuid.uuid4()
    pet_id = uuid.uuid4()
    
    mock_image_adapter.make_embedding.return_value = [0.1, 0.2, 0.3]
    mock_image_adapter.classify.return_value = pet_id
    mock_image_adapter.insert.return_value = image_id
    
    files = {"file": ("test.jpg", b"fake_image_data", "image/jpeg")}
    
    response = await async_client.post(f"/image/?user_id={user_id}", files=files)
    
    assert response.status_code == 200
    assert response.json() == str(image_id)
    
    mock_image_adapter.make_embedding.assert_called_once_with(b"fake_image_data")
    mock_image_adapter.classify.assert_called_once_with(embedding=[0.1, 0.2, 0.3], user_id=user_id)
    mock_image_adapter.insert.assert_called_once_with(embedding=[0.1, 0.2, 0.3], pet_id=pet_id, user_id=user_id)

@pytest.mark.asyncio
async def test_send_image_classification_error(async_client, mock_image_adapter):
    user_id = uuid.uuid4()
    
    mock_image_adapter.make_embedding.return_value = [0.1, 0.2, 0.3]
    mock_image_adapter.classify.return_value = None
    
    files = {"file": ("test.jpg", b"fake_image_data", "image/jpeg")}
    
    response = await async_client.post(f"/image/?user_id={user_id}", files=files)
    
    assert response.status_code == 500
    assert "Failed to process the image" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_image(async_client, mock_image_adapter):
    image_id = uuid.uuid4()
    
    response = await async_client.delete(f"/image/{image_id}")
    
    assert response.status_code == 200
    mock_image_adapter.delete.assert_called_once_with(id=image_id)

@pytest.mark.asyncio
async def test_delete_all_images(async_client, mock_image_adapter):
    response = await async_client.delete("/image/")
    
    assert response.status_code == 200
    mock_image_adapter.delete_all.assert_called_once()
