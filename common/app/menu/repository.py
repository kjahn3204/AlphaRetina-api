from typing import List

from sqlalchemy import select

from common.app.menu.entity import MenuEntity
from core.database.repostory.sqlalchemy import SQLAlchemyRepositoryBase


class MenuRepository(SQLAlchemyRepositoryBase):
    async def list(self) -> List[MenuEntity]:
        async with self.session_factory() as session:
            stmt = select(MenuEntity)
            res = await session.execute(stmt)
            rows: List[MenuEntity] = list(res.scalars().all())
        return rows
