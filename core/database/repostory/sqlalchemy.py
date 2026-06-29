from typing import Dict, Any, Callable, List

import pandas as pd
from rcore.log import logger
from rcore.model.base import TModel, PageModel, ModelBase
from sqlalchemy import text, RowMapping
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import scoped_session

from common.exception.common import DataNotFoundError
from core.database.entity.base import EntityBase
from core.database.repostory.base import IRepository, DEFAULT_PAGINATION_PAGE, DEFAULT_PAGINATION_SIZE


class SQLAlchemyRepositoryBase(IRepository):
    session: async_scoped_session

    @property
    def session_factory(self):
        return self.session.session_factory

    async def _total(self, sql: str,
                     param: Dict[str, Any] | None = None,
                     log: bool = True
                     ) -> int:
        async with self.session_factory() as session:
            sql_count = f"SELECT COUNT(*) AS CNT FROM ({sql}) T"
            if log:
                logger.info(f'count query: {sql_count}')
            res = await session.execute(text(sql_count), param)
            return int(res.scalar_one_or_none())

    async def _paginated(self, sql: str,
                         param: Dict[str, Any] | None = None,
                         mapper: Callable[[RowMapping], TModel] = None,
                         page: int | None = DEFAULT_PAGINATION_PAGE,
                         size: int | None = DEFAULT_PAGINATION_SIZE,
                         log: bool = True
                         ) -> List[TModel]:
        sql_page = f"SELECT * FROM ({sql}) T LIMIT {size} {f'OFFSET {page * size}' if page > 0 else ''}"
        if log:
            logger.info(f'paginated query: {sql_page}')
        async with self.session_factory() as session:
            res = await session.execute(text(sql_page), param)
        if mapper:
            result_page = list(map(mapper, res.mappings().all()))
        else:
            result_page = res.mappings().all()
        return result_page

    async def execute_sql(self, sql: str,
                          param: Dict[str, Any] | None = None,
                          mapper: Callable[[Any], Any] = None,
                          pagination: bool = False,
                          page: int | None = DEFAULT_PAGINATION_PAGE,
                          size: int | None = DEFAULT_PAGINATION_SIZE,
                          log: bool = True,
                          count_total: bool = True,
                          get_one:bool =False) -> PageModel[Any] | List[Any]:
        if pagination:
            if count_total:
                total = await self._total(sql, param, log)
            else:
                total = None
            result_page = await self._paginated(sql, param, mapper, page, size, log)
            return PageModel(result=result_page, page=page, size=size, count=len(result_page), total=total)
        else:
            if log:
                logger.info(f'query: {sql}')
            res = None
            try:
                async with self.session_factory() as session:
                    res = await session.execute(text(sql), param)
                logger.info(f"Code Download Complete")
            except Exception as e:
                logger.error(f"SQL 쿼리를 실행하는 동안 오류가 발생했습니다: {e}")

            if mapper and res and get_one:
                result = res.first()
                if result is None:
                    raise DataNotFoundError("")

                result = mapper(result)
            elif mapper and res :
                result = list(map(mapper, res.mappings().all()))
            elif res:
                result = res.mappings().all()
            else:
                result = []
            return result

    async def execute_sql_to_df(self, sql: str, **kwargs):
        import pandas as pd
        logger.info(f'query: {sql}')
        session = self.session()
        result = await session.run_sync(lambda s: pd.read_sql(text(sql), s.connection(), **kwargs))
        await session.close()
        return result

    async def execute_query(self, query: str,
                            param: Dict[str, Any] | None = None,
                            mapper: Callable[[Any], Any] = None,
                            log: bool = True,
                            ) -> List[Any]:
        """
        @deprecated: Use execute_sql instead
        2024.06.28 dhpark: brought from legacy, and will be deleted soon :(
        """
        if log:
            logger.debug(f'query: {query}')
        async with self.session_factory() as session:
            res = await session.execute(text(query), param)
            return list(map(mapper, res.fetchall()))

    async def change_entity(self, base_entity: EntityBase, update_object: ModelBase | EntityBase):
        if isinstance(update_object, ModelBase):
            model_et = update_object.to_entity()
        else:
            model_et = update_object
        keys = model_et.__dict__.keys()
        for key in keys:
            if key.find("_") != 0:
                val = model_et.__getattribute__(key)
                if val is not None:
                    base_entity.__setattr__(key, val)
        return base_entity


class SyncSQLAlchemyRepositoryBase(IRepository):
    session: scoped_session

    def _total(self, sql: str,
               param: Dict[str, Any] | None = None,
               log: bool = True
               ) -> int:
        sql_count = f"SELECT COUNT(*) AS CNT FROM ({sql}) T"
        if log:
            logger.info(f'count query: {sql_count}')
        res = self.session.execute(text(sql_count), param)
        return int(res.scalar_one_or_none())

    def _paginated(self, sql: str,
                   param: Dict[str, Any] | None = None,
                   mapper: Callable[[RowMapping], TModel] = None,
                   page: int | None = DEFAULT_PAGINATION_PAGE,
                   size: int | None = DEFAULT_PAGINATION_SIZE,
                   log: bool = True
                   ) -> List[TModel]:
        sql_page = f"SELECT * FROM ({sql}) T LIMIT {size} {f'OFFSET {page * size}' if page > 0 else ''}"
        if log:
            logger.info(f'paginated query: {sql_page}')
        res = self.session.execute(text(sql), param)
        if mapper:
            result_page = list(map(mapper, res.mappings().all()))
        else:
            result_page = res.mappings().all()
        return result_page

    def execute_sql(self, sql: str,
                    param: Dict[str, Any] | None = None,
                    mapper: Callable[[Any], Any] = None,
                    pagination: bool = False,
                    page: int | None = DEFAULT_PAGINATION_PAGE,
                    size: int | None = DEFAULT_PAGINATION_SIZE,
                    log: bool = True,
                    ) -> PageModel[Any] | List[Any]:
        if pagination:
            total = self._total(sql, param, log)
            result_page = self._paginated(sql, param, mapper, page, size, log)
            return PageModel(result=result_page, page=page, size=size, count=len(result_page), total=total)
        else:
            if log:
                logger.info(f'query: {sql}')
            res = self.session.execute(text(sql), param)
            result = list(map(mapper, res.mappings().all()))
            return result

    def execute_sql_to_df(self, sql: str, **kwargs) -> pd.DataFrame:
        raise NotImplementedError
