from pydantic import BaseModel
from uuid import UUID


class ScheduleCreate(BaseModel):
    user_id: UUID
    start_time: int
    end_time: int
