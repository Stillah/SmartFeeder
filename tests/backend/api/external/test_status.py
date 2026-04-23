import pytest
import datetime
from unittest.mock import AsyncMock
from backend.main import app
from backend.app.dependencies.adapters import get_feeder_status_adapter


@pytest.fixture
def mock_status_adapter():
    mock = AsyncMock()
    app.dependency_overrides[get_feeder_status_adapter] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_feeder_status_adapter, None)


@pytest.mark.asyncio
async def test_get_feeder_status(async_client, mock_status_adapter):
    now = datetime.datetime.now().isoformat()
    mock_status_adapter.get_current_food_weight.return_value = 500.0
    mock_status_adapter.get_last_connection_time.return_value = now

    response = await async_client.get("/status/")

    assert response.status_code == 200
    assert response.json() == {"current_food_weight": 500.0, "last_connection": now}

    mock_status_adapter.get_current_food_weight.assert_called_once()
    mock_status_adapter.get_last_connection_time.assert_called_once()
