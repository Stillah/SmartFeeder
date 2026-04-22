import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    pets: Mapped[list["PetModel"]] = relationship(
        "PetModel", back_populates="owner", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["ScheduleModel"]] = relationship(
        "ScheduleModel", back_populates="user", cascade="all, delete-orphan"
    )
