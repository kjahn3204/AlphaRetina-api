from dependency_injector import containers, providers

from common.app.code.repository import CodeRepository
from common.app.code.service import CodeService


class CodeContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()

    repository = providers.ThreadSafeSingleton(CodeRepository, session=core.rdb.provided.session)
    service = providers.Factory(CodeService, repository=repository)
    cache = providers.Callable(repository.provided.cache)
