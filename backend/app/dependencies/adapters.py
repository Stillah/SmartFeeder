from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.db.session import get_session
from backend.infrastructure.adapters.pet import PetsAdapter
from backend.infrastructure.adapters.feeder_status import FeederStatusAdapter
from backend.infrastructure.adapters.history import HistoryAdapter
from backend.infrastructure.adapters.images import ImageAdapter
from backend.infrastructure.adapters.time_manager import TimeManagerAdapter


def get_pets_adapter(session: AsyncSession = Depends(get_session)) -> PetsAdapter:
    return PetsAdapter(session)


def get_feeder_status_adapter(
    session: AsyncSession = Depends(get_session),
) -> FeederStatusAdapter:
    return FeederStatusAdapter(session)


def get_history_adapter(session: AsyncSession = Depends(get_session)) -> HistoryAdapter:
    return HistoryAdapter(session)


def get_image_adapter(session: AsyncSession = Depends(get_session)) -> ImageAdapter:
    return ImageAdapter(session)


def get_time_manager_adapter(
    session: AsyncSession = Depends(get_session),
) -> TimeManagerAdapter:
    return TimeManagerAdapter(session)
