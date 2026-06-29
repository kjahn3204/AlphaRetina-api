from dependency_injector import containers, providers

from app.image.repository import ImageRepository
from app.image.service import ImageService


class ImageContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()

    repository = providers.Factory(ImageRepository, session=core.rdb.provided.session)
    service = providers.Factory(ImageService,
                                repository=repository, config=config)
