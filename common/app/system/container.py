from dependency_injector import containers, providers

from common.app.system.repository import SystemRepository
from common.app.system.service import SystemService


class SystemContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()

    repository = providers.Factory(SystemRepository)
    service = providers.Factory(SystemService, repository=repository)
