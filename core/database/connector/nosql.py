import asyncio
import urllib
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import Callable

from motor.core import AgnosticDatabase, AgnosticClientSession, AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorClient
from rcore.log import logger

from core.database.connector.base import AsyncDBConnectorBase
from core.database.exception.database import NoSQLOperationError


class AsyncMongoConnector(AsyncDBConnectorBase):
    """
    _engine: motor.motor_asyncio.AsyncIOMotorClient
    """

    _engine: AsyncIOMotorClient

    _scoped_session: AgnosticClientSession
    @property
    def url(self) -> str:
        user_id = urllib.parse.quote_plus(self.config['userId'])
        password = urllib.parse.quote_plus(self.config['password'])
        host = self.config['host']
        port = self.config['port']
        database = self.config['database']
        return f'mongodb://{user_id}:{password}@{host}:{port}/?authSource={database}'

    def _pre_init_proc(self):
        pass

    def _init_engine(self) -> AsyncIOMotorClient:
        logger.debug(f'mongo client url: {self.url}')
        return AsyncIOMotorClient(self.url)

    def _post_init_proc(self):
        dbname: str = self.config['database']
        self._db: AgnosticDatabase = self._engine[dbname]

    async def _release(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._engine.close)

    @property
    def session(self) -> AgnosticClientSession:
        if not self._scoped_session:
            loop = asyncio.get_running_loop()
            self._scoped_session = loop.run_until_complete(self._db.client.start_session)
        return self._scoped_session

    async def begin(self):
        raise NotImplementedError

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError

    async def remove(self):
        await self._scoped_session.end_session()

    @asynccontextmanager
    async def session_factory(self, collection_name: str) -> Callable[..., AbstractAsyncContextManager[AgnosticClientSession, AgnosticCollection]]:
        async with await self._engine.start_session() as session:
            try:
                col = self._db[collection_name]
                yield session, col
            except Exception as e:
                raise NoSQLOperationError(e)
            finally:
                await session.end_session()
