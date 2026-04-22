import pytest
import uuid
from unittest.mock import AsyncMock
from backend.main import app
from backend.app.dependencies.adapters import get_history_adapter


@pytest.fixture
def mock_history_adapter():
    mock = AsyncMock()
    app.dependency_overrides[get_history_adapter] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_history_adapter, None)


@pytest.mark.asyncio
async def test_get_pet_history(async_client, mock_history_adapter):
    pet_id = uuid.uuid4()

    mock_history_adapter.get_food_consumption_mean.return_value = 150.5
    mock_history_adapter.get_food_consumption_std.return_value = 10.2
    mock_history_adapter.get_average_eating_times.return_value = ["08:00", "20:00"]

    response = await async_client.get(f"/history/{pet_id}")

    assert response.status_code == 200
    assert response.json() == {
        "mean": 150.5,
        "std": 10.2,
        "average_eating_times": ["08:00", "20:00"],
    }

    mock_history_adapter.get_food_consumption_mean.assert_called_once_with(pet_id)
    mock_history_adapter.get_food_consumption_std.assert_called_once_with(pet_id)
    mock_history_adapter.get_average_eating_times.assert_called_once_with(pet_id)


@pytest.mark.asyncio
async def test_get_pet_history_error(async_client, mock_history_adapter):
    pet_id = uuid.uuid4()
    mock_history_adapter.get_food_consumption_mean.side_effect = Exception("DB Error")

    response = await async_client.get(f"/history/{pet_id}")

    assert response.status_code == 500
    assert "Failed to get pet history" in response.json()["detail"]
