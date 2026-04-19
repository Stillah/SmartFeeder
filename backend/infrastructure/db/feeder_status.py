import uuid
from datetime import datetime
from sqlalchemy import Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class FeederStatusModel(Base):
    __tablename__ = "feeder_status"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    last_connection: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(datetime.timezone.utc))
    current_food_weight: Mapped[float] = mapped_column(Float, default=0.0)
