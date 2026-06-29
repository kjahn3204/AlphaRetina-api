import traceback
from abc import ABC
from contextlib import asynccontextmanager, AbstractAsyncContextManager, contextmanager, AbstractContextManager
from typing import Callable

from rcore.log import logger
from sqlalchemy import Engine, create_engine, AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncEngine, async_scoped_session, async_sessionmaker,
                                    AsyncSession)
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool

from core.database.connector.base import AsyncDBConnectorBase, SyncDBConnectorBase
from core.database.exception.database import DBOperationError
from core.database.session.context import ContextLocalSessionManager


class SyncSqlAlchemyConnector(SyncDBConnectorBase, ABC):
    _engine: Engine | None = None
    _session_maker: sessionmaker | None = None
    _scoped_session: scoped_session | None = None

    def _pre_init_proc(self):
        # self.init_context()
        pass

    def _init_engine(self):
        echo = self.config['echo']
        # echo_pool = self.config['echoPool']
        # logging_name = self.config.get('loggingName', GLOBAL_LOGGER_NAME)
        # pool_logging_name = self.config.get('poolLoggingName', GLOBAL_LOGGER_NAME)
        pool_size = self.config['poolSize']
        max_overflow = self.config['maxOverflow']
        isolation_level = self.config['isolationLevel']
        pool_pre_ping = self.config['poolPrePing']
        pool_recycle = self.config['poolRecycle']

        return create_engine(self.url,
                             echo=echo,
                             # echo_pool=echo_pool,
                             # logging_name=logging_name,
                             # pool_logging_name=pool_logging_name,
                             hide_parameters=True,
                             poolclass=QueuePool,
                             pool_size=pool_size,
                             max_overflow=max_overflow,
                             isolation_level=isolation_level,
                             pool_pre_ping=pool_pre_ping,
                             pool_recycle=pool_recycle,
                             )

    def _post_init_proc(self):
        auto_flush = self.config['autoFlush']
        auto_commit = self.config['autoCommit']
        expire_on_commit = self.config['expireOnCommit']

        self._session_maker = sessionmaker(
            bind=self._engine,
            class_=Session,
            autoflush=auto_flush,
            autocommit=auto_commit,
            expire_on_commit=expire_on_commit,
        )

        self._scoped_session = scoped_session(
            session_factory=self._session_maker,
        )

    def _release(self):
        self.session.close_all()
        self._engine.dispose()

    def begin(self):
        self.session.begin()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def remove(self):
        self.session.close()
        self.session.remove()

    @contextmanager
    def session_factory(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(traceback.format_exc())
            session.rollback()
            raise DBOperationError(self.__class__.__name__, e)
        finally:
            session.close()


class AsyncSqlAlchemyConnector(AsyncDBConnectorBase, ContextLocalSessionManager, ABC):
    _engine: AsyncEngine | None = None
    _session_maker: async_sessionmaker | None = None
    _scoped_session: async_scoped_session | None = None

    def _pre_init_proc(self):
        self.init_context()

    def _init_engine(self):
        echo = self.config['echo']
        # echo_pool = self.config['echoPool']
        # logging_name = self.config.get('loggingName', GLOBAL_LOGGER_NAME)
        # pool_logging_name = self.config.get('poolLoggingName', GLOBAL_LOGGER_NAME)
        pool_size = self.config['poolSize']
        max_overflow = self.config['maxOverflow']
        isolation_level = self.config['isolationLevel']
        pool_pre_ping = self.config.get('poolPrePing')
        pool_recycle = self.config['poolRecycle'] if not pool_pre_ping else -1

        return create_async_engine(self.url,
                                   echo=echo,
                                   # echo_pool=echo_pool,
                                   # logging_name=logging_name,
                                   # pool_logging_name=pool_logging_name,
                                   poolclass=AsyncAdaptedQueuePool,
                                   hide_parameters=True,
                                   pool_size=pool_size,
                                   max_overflow=max_overflow,
                                   isolation_level=isolation_level,
                                   pool_pre_ping=pool_pre_ping,
                                   pool_recycle=pool_recycle,
                                   )

    def _post_init_proc(self):
        auto_flush = self.config['autoFlush']
        auto_commit = self.config['autoCommit']
        expire_on_commit = self.config['expireOnCommit']

        self._session_maker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autoflush=auto_flush,
            autocommit=auto_commit,
            expire_on_commit=expire_on_commit,
        )

        self._scoped_session = async_scoped_session(
            session_factory=self._session_maker,
            scopefunc=self._scope_func
        )

    async def _release(self):
        await self.session.close_all()
        await self._engine.dispose()

    async def begin(self):
        await self.session.begin()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def remove(self):
        await self.session.remove()
        await self.session.close()

    @asynccontextmanager
    async def session_factory(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_maker()
        try:
            yield session
        except Exception as e:
            logger.error(traceback.format_exc())
            await session.rollback()
            raise DBOperationError(self.__class__.__name__, e)
        finally:
            await session.close()
