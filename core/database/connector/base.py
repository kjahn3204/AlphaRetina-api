import asyncio
from abc import abstractmethod, ABC
from contextlib import asynccontextmanager
from typing import Any, Dict

from rcore.log import logger

from core.database.exception.database import DBConfigurationError, DBConnectorInitError, SessionNotInitializedError


async def release_db_conn(*conns):
    awaitables = []
    for conn in conns:
        awaitables.append(conn.release())
    await asyncio.gather(*awaitables)


class DBConnectorBase(ABC):
    config: Any
    _engine: Any | None = None
    _session_maker: Any | None = None
    _scoped_session: Any | None = None
    _session: Any | None = None

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def _pre_init_proc(self):
        pass

    @abstractmethod
    def _init_engine(self):
        pass

    @abstractmethod
    def _post_init_proc(self):
        pass

    @property
    def session(self):
        if not self._scoped_session:
            raise SessionNotInitializedError()
        return self._scoped_session


class SyncDBConnectorBase(DBConnectorBase):
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        cnf_app_db: Dict = config['app']['db'][name]
        cnf_core_db: Dict = config['core']['db'][cnf_app_db['kind']]
        cnf_core_db.update(cnf_app_db)
        self.config = cnf_core_db
        logger.debug(f'Sync DBConnector ({name}) initializing... config: {self.config}')
        try:
            self._pre_init_proc()
            self._engine = self._init_engine()
            self._post_init_proc()
        except KeyError as e:
            raise DBConfigurationError(str(e), self.config)
        except Exception as e:
            raise DBConnectorInitError(self.name, e)

    def release(self):
        logger.debug(f'Sync DBConnector {self.name} releasing...')
        self._release()
        logger.debug(f'Sync DBConnector {self.name} released.')

    @abstractmethod
    def _release(self):
        pass

    @abstractmethod
    def begin(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    @asynccontextmanager
    def session_factory(self):
        pass


class AsyncDBConnectorBase(DBConnectorBase):
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        cnf_app_db: Dict = config['app']['db'][name]
        cnf_core_db: Dict = config['core']['db'][cnf_app_db['kind']]
        cnf_core_db.update(cnf_app_db)
        self.config = cnf_core_db
        logger.debug(f'Async DBConnector ({name}) initializing... config: {self.config}')
        try:
            self._pre_init_proc()
            self._engine = self._init_engine()
            self._post_init_proc()
        except KeyError as e:
            raise DBConfigurationError(str(e), self.config)
        except Exception as e:
            raise DBConnectorInitError(str(cnf_app_db['kind']), e)

    async def release(self):
        logger.debug(f'Async DBConnector {self.name} releasing...')
        await self._release()
        logger.debug(f'Async DBConnector {self.name} released.')

    @abstractmethod
    async def _release(self):
        pass

    @abstractmethod
    async def begin(self):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def remove(self):
        pass

    @abstractmethod
    @asynccontextmanager
    async def session_factory(self):
        pass
