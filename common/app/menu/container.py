from dependency_injector import containers, providers

from common.app.menu.repository import MenuRepository
from common.app.menu.service import MenuService


class MenuContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    code = providers.DependenciesContainer()
    config = providers.Configuration()

    repository = providers.Factory(MenuRepository, session=core.rdb.provided.session)
    service = providers.Factory(MenuService, repository=repository, code_service=code.service)
