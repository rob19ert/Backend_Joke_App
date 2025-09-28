import asyncio
from typing import Optional
import typing
from app.crm.model import Base
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application

url = "postgresql+asyncpg://postgres:admin@localhost/jokes"

class Database:
    def __init__(self, app: "Application") -> None:
        self.app = app
        self.engine: Optional[AsyncEngine] = None
        self.session: Optional[async_sessionmaker[AsyncSession]]  = None


    async def connect(self, app: "Application") -> None:
        self.engine = create_async_engine(url, echo = True)
        self.session = async_sessionmaker(self.engine, expire_on_commit = False)
        print('connect to database')

    async def disconnect(self, app: "Application") -> None:
        if self.engine:
            await self.engine.dispose()
            print('disconnect from database')