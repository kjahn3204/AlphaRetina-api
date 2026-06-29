from dependency_injector import containers, providers

from app.examination.repository import ExamRepository
from app.examination.service import ExamService
from app.patient.repository import PatientRepository
from app.patient.service import PatientService


class ExamContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()
    image = providers.DependenciesContainer()

    repository = providers.Factory(ExamRepository, session=core.rdb.provided.session)
    service = providers.Factory(ExamService,
                                repository=repository, image_repository=image.repository)
