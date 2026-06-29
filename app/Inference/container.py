from dependency_injector import containers, providers

from ai.model import SegmentationModel
from app.Inference.repository import InfRepository
from app.Inference.service import InfService


class InfContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()
    image = providers.DependenciesContainer()
    exam = providers.DependenciesContainer()
    code = providers.DependenciesContainer()

    ai = providers.ThreadSafeSingleton(SegmentationModel, config=config)
    repository = providers.Factory(InfRepository, session=core.rdb.provided.session)
    service = providers.Factory(InfService, ai = ai,
                                repository=repository, image_repository=image.repository, exam_repository=exam.repository, code_repository=code.repository, config=config)
