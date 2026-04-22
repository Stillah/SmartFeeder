import uuid
import datetime
from datetime import datetime as dt
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .base import Base


class ImageModel(Base):
    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pets.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(512))
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[dt] = mapped_column(DateTime(timezone=True), default=lambda: dt.now(datetime.UTC))

    pet: Mapped["PetModel"] = relationship("PetModel", back_populates="images")
    user: Mapped["UserModel"] = relationship("UserModel")

