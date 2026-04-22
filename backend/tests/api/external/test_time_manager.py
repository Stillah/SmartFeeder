import pytest
import uuid
from unittest.mock import AsyncMock
from backend.main import app
from backend.app.dependencies.adapters import get_time_manager_adapter

@pytest.fixture
def mock_time_manager_adapter():
    mock = AsyncMock()
    app.dependency_overrides[get_time_manager_adapter] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_time_manager_adapter, None)

@pytest.mark.asyncio
async def test_add_schedule(async_client, mock_time_manager_adapter):
    user_id = uuid.uuid4()
    payload = {
        "user_id": str(user_id),
        "start_time": 3600,
        "end_time": 7200
    }
    
    response = await async_client.post("/schedules/", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_time_manager_adapter.add.assert_called_once_with(user_id, 3600, 7200)

@pytest.mark.asyncio
async def test_get_schedules(async_client, mock_time_manager_adapter):
    user_id = uuid.uuid4()
    mock_schedules = [
        {"id": str(uuid.uuid4()), "start_time": 3600, "end_time": 7200}
    ]
    mock_time_manager_adapter.load_all.return_value = mock_schedules
    
    response = await async_client.get(f"/schedules/{user_id}")
    
    assert response.status_code == 200
    assert response.json() == {"schedules": mock_schedules}
    mock_time_manager_adapter.load_all.assert_called_once_with(user_id)
