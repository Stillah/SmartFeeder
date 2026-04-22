import uuid
import datetime
from datetime import datetime as dt
from sqlalchemy import ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class LogsModel(Base):
    __tablename__ = "feeding_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pets.id"), index=True)
    timestamp: Mapped[dt] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.now(datetime.UTC)
    )
    amount_eaten: Mapped[float] = mapped_column(Float)

    pet: Mapped["PetModel"] = relationship("PetModel", back_populates="feeding_logs")
