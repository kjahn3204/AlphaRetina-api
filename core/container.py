from dependency_injector import containers, providers

from rcore.log import logger


class CoreContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # db connectors
    try:
        from core.database.connector.base import release_db_conn
        from core.database.connector.rdb import AsyncMysqlConnector
        from core.database.session.context import set_context, reset_context

        rdb = providers.Singleton(AsyncMysqlConnector, name='rdb', config=config)

        set_context = providers.Callable(set_context, rdb)
        reset_context = providers.Callable(reset_context, rdb)
        release_db = providers.Callable(release_db_conn, rdb)

    except ImportError as e:
        logger.warning(f'Could not find core.database module ::: {e}')
