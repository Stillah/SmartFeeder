import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from backend.main import app
from backend.app.dependencies.adapters import get_pets_adapter


@pytest.fixture
def mock_pets_adapter():
    mock = AsyncMock()
    app.dependency_overrides[get_pets_adapter] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_pets_adapter, None)


@pytest.mark.asyncio
async def test_create_pet(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    mock_pets_adapter.add.return_value = pet_id

    owner_id = uuid.uuid4()
    payload = {
        "owner_id": str(owner_id),
        "name": "Barsik",
        "weight": 4.5,
        "age": 3,
        "breed": "British",
        "target_portion": 100.0,
    }

    response = await async_client.post("/pets/", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": str(pet_id)}
    mock_pets_adapter.add.assert_called_once()


@pytest.mark.asyncio
async def test_get_pet(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    mock_pet = {"id": str(pet_id), "name": "Barsik"}
    mock_pets_adapter.load.return_value = mock_pet

    response = await async_client.get(f"/pets/{pet_id}")

    assert response.status_code == 200
    assert response.json() == mock_pet
    mock_pets_adapter.load.assert_called_once_with(pet_id)


@pytest.mark.asyncio
async def test_get_pet_not_found(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    mock_pets_adapter.load.return_value = None

    response = await async_client.get(f"/pets/{pet_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Pet not found"}

@pytest.mark.asyncio
async def test_update_pet(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    payload = {
        "name": "Barsik Updated",
        "weight": 5.0
    }
    
    response = await async_client.put(f"/pets/{pet_id}", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_pets_adapter.update.assert_called_once_with(pet_id, name="Barsik Updated", weight=5.0)

@pytest.mark.asyncio
async def test_update_pet_error(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    mock_pets_adapter.update.side_effect = Exception("DB Error")
    
    response = await async_client.put(f"/pets/{pet_id}", json={"name": "Barsik"})
    
    assert response.status_code == 500
    assert "Failed to update pet" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_pet(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    
    response = await async_client.delete(f"/pets/{pet_id}")
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_pets_adapter.delete.assert_called_once_with(pet_id)

@pytest.mark.asyncio
async def test_delete_pet_error(async_client, mock_pets_adapter):
    pet_id = uuid.uuid4()
    mock_pets_adapter.delete.side_effect = Exception("DB Error")
    
    response = await async_client.delete(f"/pets/{pet_id}")
    
    assert response.status_code == 500
    assert "Failed to delete pet" in response.json()["detail"]
