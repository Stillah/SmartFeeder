import uuid
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class PetModel(Base):
    __tablename__ = "pets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    breed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_portion: Mapped[float | None] = mapped_column(Float, nullable=True)

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="pets")
    images: Mapped[list["ImageModel"]] = relationship("ImageModel", back_populates="pet", cascade="all, delete-orphan")
    feeding_logs: Mapped[list["LogsModel"]] = relationship("LogsModel", back_populates="pet", cascade="all, delete-orphan")
