from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.interfaces.timer_manager import TimeManagmentInterface
from backend.infrastructure.db.schedule import ScheduleModel


@dataclass
class TimeManagerAdapter(TimeManagmentInterface):
    session: AsyncSession

    async def add(self, user_id: UUID, start: int, end: int) -> None:
        schedule = ScheduleModel(user_id=user_id, start_time=start, end_time=end)
        self.session.add(schedule)
        await self.session.commit()

    async def load_all(self, user_id: UUID) -> list[tuple[int, int]]:
        stmt = select(ScheduleModel).where(ScheduleModel.user_id == user_id)
        result = await self.session.execute(stmt)
        schedules = result.scalars().all()
        return [(s.start_time, s.end_time) for s in schedules]

    async def update(
        self,
        user_id: UUID,
        old_start: int,
        old_end: int,
        new_start: int | None,
        new_end: int | None,
    ) -> None:
        stmt = select(ScheduleModel).where(
            ScheduleModel.user_id == user_id,
            ScheduleModel.start_time == old_start,
            ScheduleModel.end_time == old_end,
        )
        result = await self.session.execute(stmt)
        schedule = result.scalar_one_or_none()

        if schedule:
            if new_start is not None:
                schedule.start_time = new_start
            if new_end is not None:
                schedule.end_time = new_end
            await self.session.commit()

    async def delete(self, user_id: UUID, start: int, end: int) -> None:
        stmt = delete(ScheduleModel).where(
            ScheduleModel.user_id == user_id,
            ScheduleModel.start_time == start,
            ScheduleModel.end_time == end,
        )
        await self.session.execute(stmt)
        await self.session.commit()
