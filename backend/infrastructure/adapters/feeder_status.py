from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.interfaces.feeder_status import FeederStatusInterface
from backend.infrastructure.db.feeder_status import FeederStatusModel


@dataclass
class FeederStatusAdapter(FeederStatusInterface):
    session: AsyncSession

    async def _get_or_create_status(self) -> FeederStatusModel:
        status = await self.session.get(FeederStatusModel, 1)
        if not status:
            status = FeederStatusModel(id=1, current_food_weight=0.0)
            self.session.add(status)
            await self.session.commit()
            await self.session.refresh(status)
        return status

    async def get_last_connection_time(self) -> datetime:
        status = await self._get_or_create_status()
        return status.last_connection

    async def get_current_food_weight(self) -> float:
        status = await self._get_or_create_status()
        return status.current_food_weight

    async def update_feeder_weight(self, new_weight: float) -> None:
        status = await self._get_or_create_status()
        status.current_food_weight = new_weight
        await self.session.commit()

    async def update_connection_time(self) -> None:
        status = await self._get_or_create_status()
        status.last_connection = datetime.now(datetime.timezone.utc)
        await self.session.commit()
