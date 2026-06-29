from dependency_injector import containers, providers

from common.app.auth.service import AuthService


class AuthContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    service = providers.Factory(AuthService, config=config.api.auth)
