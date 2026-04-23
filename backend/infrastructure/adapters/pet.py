from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.interfaces.pet import PetsInterface
from backend.infrastructure.db.pet import PetModel


@dataclass
class PetsAdapter(PetsInterface):
    session: AsyncSession

    async def add(
        self,
        owner_id: UUID,
        name: str = "Unnamed cat",
        weight: float | None = None,
        age: int | None = None,
        breed: str | None = None,
        target_portion: float | None = None,
    ) -> UUID:
        pet = PetModel(
            owner_id=owner_id,
            name=name,
            weight=weight,
            age=age,
            breed=breed,
            target_portion=target_portion,
        )
        self.session.add(pet)
        await self.session.commit()
        await self.session.refresh(pet)
        return pet.id

    async def load(self, id: UUID) -> PetModel:
        pet = await self.session.get(PetModel, id)
        if not pet:
            raise ValueError(f"Pet with id {id} not found")
        return pet

    async def get_by_owner_id(self, owner_id: UUID) -> list[PetModel]:
        stmt = select(PetModel).where(PetModel.owner_id == owner_id)
        result = await self.session.execute(stmt)
        pets = result.scalars().all()
        return pets

    async def update(self, id: UUID, **kwargs) -> None:
        if not kwargs:
            return
        stmt = update(PetModel).where(PetModel.id == id).values(**kwargs)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, id: UUID) -> None:
        stmt = delete(PetModel).where(PetModel.id == id)
        await self.session.execute(stmt)
        await self.session.commit()
