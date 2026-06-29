from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from rcore.constant import DEPLOY_MODE
from rcore.di.wiring import autowire
from rcore.exception.base import RapidException
from rcore.log import setup_logging

from app.Inference.router import inf_router
from app.container import ApplicationContainer
from app.examination.router import exam_router
from app.image.router import image_router
from app.patient.router import patient_router
from common.app.auth.exception import CredentialsException
from common.app.auth.router import auth_router
from common.app.code.router import code_router
from common.app.menu.router import menu_router
from common.app.system.router import system_router
from common.app.user.router import user_router
from common.core.fastapi.mount import init_mounts
from common.core.fastapi.router import init_routers
from common.core.middleware.auth import create_auth_middleware
from common.core.middleware.cors import create_cors_middleware
from common.core.middleware.sqlalchemy import create_sqlalchemy_middleware
from common.events.lifespan import base_lifespan
from common.exception.exception_handlers import (http_exception_handler, request_validation_exception_handler,
                                                 credentials_exception_handler, unhandled_exception_handler,
                                                 rapid_exception_handler)


def create_app() -> FastAPI:
    container = ApplicationContainer()
    config = container.config()
    cnf_core = config.get('core')
    cnf_api = config.get('api')

    setup_logging(cnf_core.get('log'))
    autowire(container, cnf_core.get('di').get('wiring'))

    _app = FastAPI(
        lifespan=base_lifespan,
        docs_url=None if DEPLOY_MODE == 'prod' else '/docs',
        redoc_url=None if DEPLOY_MODE == 'prod' else '/redoc',
        middleware=[
            create_cors_middleware(cnf_api.get('cors')),
            create_auth_middleware(),
            create_sqlalchemy_middleware(),
        ],
        exception_handlers={
            HTTPException: http_exception_handler,
            RequestValidationError: request_validation_exception_handler,
            CredentialsException: credentials_exception_handler,
            RapidException: rapid_exception_handler,
            Exception: unhandled_exception_handler,
        }
    )
    _app.container = container

    init_routers(_app, [
        auth_router,
        system_router,
        code_router,
        menu_router,
        user_router,
        patient_router,
        exam_router,
        image_router,
        inf_router

    ])
    init_mounts(_app, cnf_api.get('mount'))

    return _app


app = create_app()
