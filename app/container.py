from dependency_injector import containers, providers
from rcore.constant import CORE_CONFIG_PATH

from app.Inference.container import InfContainer
from app.constant import BASE_CONFIG_PATH, CONFIG_PATH
from app.examination.container import ExamContainer
from app.image.container import ImageContainer
from app.patient.container import PatientContainer
from common.constant import COMMON_CONFIG_PATH
from common.container import CommonContainer
from core.container import CoreContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    dhpark: Inversion of Control Container.
    implemented by Dependency Injector
    """

    config = providers.Configuration(
        yaml_files=[CORE_CONFIG_PATH, COMMON_CONFIG_PATH, BASE_CONFIG_PATH, CONFIG_PATH],
        strict=True,
    )

    core = providers.Container(CoreContainer, config=config)
    common = providers.Container(CommonContainer, config=config, core=core)

    image = providers.Container(ImageContainer, config=config, core=core)
    exam = providers.Container(ExamContainer, config=config, core=core, image=image)
    patient = providers.Container(PatientContainer, config=config, core=core, exam=exam)
    inference = providers.Container(InfContainer, config=config, core=core, image=image, exam=exam, code=common.code)