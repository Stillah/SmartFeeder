import os
import uuid
import random
import datetime
import logging
from sqlalchemy import select
from backend.infrastructure.db.session import async_session_maker
from backend.infrastructure.db.user import UserModel
from backend.infrastructure.db.pet import PetModel
from backend.infrastructure.db.schedule import ScheduleModel
from backend.infrastructure.db.feeder_status import FeederStatusModel
from backend.infrastructure.db.log import LogsModel
from backend.infrastructure.db.image import ImageModel

logger = logging.getLogger(__name__)


async def seed_db():
    logger.info("Checking if database needs seeding...")
    async with async_session_maker() as session:
        # Проверяем, есть ли уже пользователи в базе
        result = await session.execute(select(UserModel).limit(1))
        existing_user = result.scalars().first()

        # if existing_user:
        #     logger.info("Database is already seeded. Skipping.")
        #     return

        logger.info("Seeding database with test data...")

        # Создаем тестового пользователя
        test_user_id = uuid.uuid4()
        test_user = UserModel(id=test_user_id, is_active=True)
        session.add(test_user)

        # Создаем тестового питомца
        test_pet_id = uuid.uuid4()
        test_pet = PetModel(
            id=test_pet_id,
            owner_id=test_user_id,
            name="Barsik",
            weight=4.5,
            age=3,
            breed="British Shorthair",
            target_portion=150.0,
        )
        session.add(test_pet)

        # Создаем тестовое расписание (например, с 08:00 до 09:00)
        # Время хранится в секундах от начала дня
        test_schedule = ScheduleModel(
            user_id=test_user_id,
            start_time=28800,  # 08:00 AM
            end_time=32400,  # 09:00 AM
        )
        session.add(test_schedule)

        # Создаем статус кормушки
        feeder_status = FeederStatusModel(
            id=1,
            last_connection=datetime.datetime.now(datetime.UTC),
            current_food_weight=500.0,
        )
        # Проверяем, есть ли уже статус кормушки
        status_result = await session.execute(select(FeederStatusModel).limit(1))
        if not status_result.scalars().first():
            session.add(feeder_status)

        # Создаем логи кормления для статистики (истории)
        log1 = LogsModel(
            pet_id=test_pet_id,
            amount_eaten=50.0,
            timestamp=datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1),
        )
        log2 = LogsModel(
            pet_id=test_pet_id,
            amount_eaten=45.0,
            timestamp=datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=2),
        )
        session.add_all([log1, log2])

        # Создаем тестовые изображения и эмбеддинги
        storage_dir = "storage/images"
        os.makedirs(storage_dir, exist_ok=True)

        # Минимальный валидный GIF 1x1 пиксель (прозрачный) для тестов
        tiny_gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"

        images = []
        for i in range(3):
            img_id = uuid.uuid4()
            filename = f"{img_id}.gif"
            filepath = os.path.join(storage_dir, filename)

            with open(filepath, "wb") as f:
                f.write(tiny_gif)

            # Генерируем случайный эмбеддинг (512 размерность)
            embedding = [random.uniform(-1.0, 1.0) for _ in range(512)]

            img_model = ImageModel(
                id=img_id,
                pet_id=test_pet_id,
                user_id=test_user_id,
                embedding=embedding,
                image_path=filepath,
                timestamp=datetime.datetime.now(datetime.UTC)
                - datetime.timedelta(hours=i),
            )
            images.append(img_model)

        session.add_all(images)

        await session.commit()

        logger.info("Database seeded successfully!")
        logger.info(f"--- TEST DATA ---")
        logger.info(f"Test User ID: {test_user_id}")
        logger.info(f"Test Pet ID: {test_pet_id}")
        logger.info(f"Generated 3 test images in {storage_dir}")
        logger.info(f"-----------------")
