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
async def test_get_pet_analysis(async_client, mock_history_adapter):
    pet_id = uuid.uuid4()

    mock_history_adapter.get_analysis.return_value = {
        "mean": 150.5,
        "std": 10.2,
        "average_eating_times": [8.0, 20.0],
    }

    response = await async_client.get(f"/history/{pet_id}/analysis")

    assert response.status_code == 200
    assert response.json() == {
        "mean": 150.5,
        "std": 10.2,
        "average_eating_times": [8.0, 20.0],
    }

    mock_history_adapter.get_analysis.assert_called_once_with(pet_id)


@pytest.mark.asyncio
async def test_get_pet_analysis_error(async_client, mock_history_adapter):
    pet_id = uuid.uuid4()
    mock_history_adapter.get_analysis.side_effect = Exception("DB Error")

    response = await async_client.get(f"/history/{pet_id}/analysis")

    assert response.status_code == 500
    assert "Failed to get pet analysis" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_recent_feedings(async_client, mock_history_adapter):
    pet_id = uuid.uuid4()
    log_id = uuid.uuid4()

    mock_history_adapter.get_recent_feedings.return_value = [
        {
            "id": str(log_id),
            "pet_id": str(pet_id),
            "timestamp": "2023-01-01T12:00:00Z",
            "amount_eaten": 50.0,
        }
    ]

    response = await async_client.get(f"/history/{pet_id}/recent?limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(log_id)

    mock_history_adapter.get_recent_feedings.assert_called_once_with(pet_id, 5)


@pytest.mark.asyncio
async def test_get_recent_feedings_error(async_client, mock_history_adapter):
    pet_id = uuid.uuid4()
    mock_history_adapter.get_recent_feedings.side_effect = Exception("DB Error")

    response = await async_client.get(f"/history/{pet_id}/recent")

    assert response.status_code == 500
    assert "Failed to get recent feedings" in response.json()["detail"]
