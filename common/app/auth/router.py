from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm

from common.app.auth.model import Token
from common.app.auth.service import AuthService
from common.app.user.exception import UserNotFoundError
from common.app.user.model import LoginUser
from common.app.user.service import UserService
from common.core.fastapi.router import LoggingAPIRoute

auth_router = APIRouter(prefix='', tags=['base'], route_class=LoggingAPIRoute)


@auth_router.post("/signin")
@inject
async def signin(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                 user_service: UserService = Depends(Provide['common.user.service']),
                 ) -> Token:
    return await user_service.get_token(form_data)


@auth_router.get("/me")
@inject
async def get_my_info(request: Request) -> LoginUser:
    user: LoginUser = request.state.user
    if user is None:
        raise UserNotFoundError(user)
    return user


@auth_router.get("/refresh")
@inject
async def refresh_credentials(request: Request,
                              user_service: UserService = Depends(Provide['common.user.service']),
                              auth_service: AuthService = Depends(Provide['common.auth.service']),
                              ) -> Token:
    login_user = await user_service.get_login_user(request.state.user.id)
    if login_user is None:
        raise UserNotFoundError(login_user)
    return auth_service.refresh_token(request.state.token)

