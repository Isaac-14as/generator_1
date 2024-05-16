import asyncio
import datetime
import random
import math
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, delete, insert, select, update, text

# DB_HOST='localhost'
# DB_PORT='5432'
# DB_USER='postgres'
# DB_PASS='postgres'
# DB_NAME='diploma_db'


DB_HOST='db'
DB_PORT=5432
DB_USER='postgres'
DB_PASS='postgres'
DB_NAME='app_db'





DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async_engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class ValueDevice(Base):
    __tablename__ = 'value_device'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_power: Mapped[float | None]
    active_power: Mapped[float | None]
    reactive_power: Mapped[float | None]
    voltage: Mapped[float | None]
    amperage: Mapped[float | None]
    power_factor: Mapped[float | None]
    date_of_collection: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    device_id: Mapped[int]


class AccidentLog(Base):
    __tablename__ = 'accident_log'

    id: Mapped[int] = mapped_column(primary_key=True)
    info: Mapped[str]
    date_of_origin: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    device_id: Mapped[int]


async def add_value(data):
    async with async_session_maker() as session:
        query = insert(ValueDevice).values(**data)
        await session.execute(query)
        await session.commit()

async def add_accident(data):
    async with async_session_maker() as session:
        query = insert(AccidentLog).values(**data)
        await session.execute(query)
        await session.commit()


async def print_numbers():
    accident_count = [i * 10 for i in range(4)]
    while True:
        amperage = [round(random.uniform(5.2, 5.4), 1) for _ in range(4)]
        voltage = [random.randint(209, 231) * 1000 for _ in range(4)]
        power_factor = [round(random.uniform(0.8, 0.95), 2) for _ in range(4)]
  
        for i in range(4):
            accident_count[i] += 1
            if accident_count[i] > 60:
                voltage[i] = random.randint(195, 245) * 1000
            data = {
                'full_power': round(amperage[i] * voltage[i] / 10**6, 2),
                'active_power': round((amperage[i] * voltage[i] * power_factor[i]) / 10**6, 2),
                'reactive_power': round((amperage[i] * voltage[i] * (1 - (power_factor[i] ** 2)) ** (1/2)) / 10**6, 2),
                'voltage': voltage[i] // 1000,
                'amperage': amperage[i],
                'power_factor': power_factor[i],
                'device_id': i + 1
            }
            if voltage[i] // 1000 < 200:
                data_accident = {
                    'info': f"Зафиксировано напряжение меньше 200 кВ (S = {data['full_power']} МВА, P = {data['active_power']} МВт, Q = {data['reactive_power']} МВар, U = {data['voltage']} А, I = {data['amperage']} А, cos(φ) = {data['power_factor']})",
                    'device_id': i + 1
                }
                accident_count[i] = 0
                await add_accident(data_accident)
            elif voltage[i] // 1000 > 240:
                data_accident = {
                    'info': f"Зафиксировано напряжение больше 240 кВ (S = {data['full_power']} МВА, P = {data['active_power']} МВт, Q = {data['reactive_power']} МВар, U = {data['voltage']} А, I = {data['amperage']} А, cos(φ) = {data['power_factor']})",
                    'device_id': i + 1
                }
                await add_accident(data_accident)
                accident_count[i] = 0

            await add_value(data)
        await asyncio.sleep(3)

async def main():
    task = asyncio.create_task(print_numbers())
    await task

asyncio.run(main())