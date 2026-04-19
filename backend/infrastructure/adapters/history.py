from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.interfaces.history import HistoryInterface
from backend.infrastructure.db.log import LogsModel

@dataclass
class HistoryAdapter(HistoryInterface):
    session: AsyncSession

    async def get_food_consumption_mean(self, pet_id: UUID) -> float:
        stmt = select(func.avg(LogsModel.amount_eaten)).where(LogsModel.pet_id == pet_id)
        result = await self.session.execute(stmt)
        mean = result.scalar()
        return float(mean) if mean is not None else 0.0

    async def get_food_consumption_std(self, pet_id: UUID) -> float:
        stmt = select(func.stddev(LogsModel.amount_eaten)).where(LogsModel.pet_id == pet_id)
        result = await self.session.execute(stmt)
        std = result.scalar()
        return float(std) if std is not None else 0.0

    async def get_average_eating_times(self, pet_id: UUID) -> list[float]:
        stmt = select(LogsModel.timestamp).where(LogsModel.pet_id == pet_id)
        result = await self.session.execute(stmt)
        times = []
        for (timestamp,) in result.all():
            hour_float = timestamp.hour + timestamp.minute / 60.0
            times.append(hour_float)
        return times

    async def add_feeding_log(self, pet_id: UUID, amount_eaten: float) -> None:
        log = LogsModel(pet_id=pet_id, amount_eaten=amount_eaten)
        self.session.add(log)
        await self.session.commit()
