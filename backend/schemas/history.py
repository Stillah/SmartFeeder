from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List

class FeedingLogResponse(BaseModel):
    id: UUID
    pet_id: UUID
    timestamp: datetime
    amount_eaten: float

    model_config = ConfigDict(from_attributes=True)

class AnalysisResponse(BaseModel):
    mean: float
    std: float
    average_eating_times: List[float]
