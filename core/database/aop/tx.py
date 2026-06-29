import inspect

from dependency_injector.wiring import inject, Provide
from rcore.log import logger

from core.database.connector.base import AsyncDBConnectorBase
from core.database.exception.database import DBOperationError


def transactional(conn: str):
    def _transactional(func):
        is_async: bool = inspect.iscoroutinefunction(func)
        if is_async:
            @inject
            async def async_fn_wrapper(*args,
                                       dbconn: AsyncDBConnectorBase = Provide[f'core.{conn}'],
                                       **kwargs):
                # before calling src func
                logger.info(f'@transactional - original func: {func.__name__}()')

                try:
                    ret = await func(*args, **kwargs)
                    await dbconn.commit()
                except Exception as e:
                    await dbconn.rollback()
                    raise DBOperationError(dbconn.name, e)
                finally:
                    await dbconn.remove()

                # after calling src func
                return ret

            return async_fn_wrapper

        else:
            @inject
            def sync_fn_wrapper(*args,
                                dbconn: AsyncDBConnectorBase = Provide[f'core.{conn}'],
                                **kwargs):
                # before calling src func
                logger.info(f'@transactional - original func: {func.__name__}()')

                try:
                    ret = func(*args, **kwargs)
                    dbconn.commit()
                except Exception as e:
                    dbconn.rollback()
                    raise DBOperationError(dbconn.name, e)
                finally:
                    dbconn.remove()

                # after calling src func
                return ret

            return sync_fn_wrapper

    return _transactional
