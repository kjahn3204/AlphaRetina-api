import pytest
from dependency_injector.wiring import inject, Provide
from jose import jwt
from pytest import fixture
from rcore.constant import DEPLOY_MODE

from app.analytics.service.event import AnalyticsService
from app.container import ApplicationContainer
from common.app.auth.service import AuthService
from common.app.user.model import LoginUser
from common.app.user.service import UserService
from common.util.config import check_url_wildcard
from common.util.date import str_to_dt, now, dt_to_str
from core.database.aop.context import acontext

'''
PyTest Template for Dependency Injector
2023-05-02 dhpark:
dependency injector의 ioc container를 load하여 pytest를 진행하려면 본 템플릿을 사용하세요.

'''


@fixture(scope='module', autouse=True)
def container():
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    return container


@pytest.mark.asyncio
@acontext
@inject
async def test_get_eternal_token(user_service: UserService = Provide['common.user.service']):
    admin_user = await user_service.get_login_user('admin')
    # secret_key = JWT_SECRET_KEY
    secret_key = f'knejwt{DEPLOY_MODE}qwer'
    to_encode = admin_user.model_dump()
    to_encode["exp"] = str_to_dt('9999-12-31 00:00:00')
    encoded_jwt = jwt.encode(to_encode, secret_key)
    print(f'>>> secret key: {secret_key}')
    print(f'>>> eternal token for {admin_user.id}({admin_user.name}) : {encoded_jwt}')


@pytest.mark.asyncio
@inject
async def test_auth(auth_service: AuthService = Provide['common.auth.service'],
                    user_service: UserService = Provide['common.user.service'],
                    ) -> None:
    src_user_info = {'id': 'dhpark'}
    token = auth_service.create_access_token(src_user_info, 0)
    assert len(token) > 0

    user_info = auth_service.get_auth_user_from_token(token)
    print(user_info)

    login_user: LoginUser = await user_service.get_login_user(user_info['id'])
    assert login_user.name == '박대환'

    print(token)


def test_jwt_decode():
    # secret_key = JWT_SECRET_KEY
    from common.constant import JWT_REFRESH_SECRET_KEY
    secret_key = JWT_REFRESH_SECRET_KEY
    # secret_key = f'knejwt{DEPLOY_MODE}qwer'
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImRocGFya0BrbmVuZXJneS5jby5rciIsIm5hbWUiOiJcdWJjMTVcdWIzMDBcdWQ2NTgiLCJpc19hY3RpdmUiOnRydWUsInBvc2l0aW9uIjpudWxsLCJyb2xlcyI6WyJBRE0iLCJERVYiXSwiZXhwIjoxNzE2ODkxNjA1fQ.HnfHPh-W5q2FrvNbNyQYQTtOJFBgBuihbT-MYLAhWGA'
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    print(payload)


def test_allow_url():
    urls = ['/', '/signin', '/status', '/docs', '/favicon.ico', '/static/**/favicon.ico', '/openapi.json']
    target_url = '/static/a/b/c/favicon.ico'

    print(check_url_wildcard(urls, target_url))


@pytest.mark.asyncio
@inject
async def test_user_event_ignore_by_user_id(analytics_service: AnalyticsService = Provide['analytics.service'],
                                            user_service: UserService = Provide['common.user.service'],
                                            ):
    login_user = await user_service.get_login_user('cs@knenergy.co.kr')
    res = await analytics_service.log_event(dt_to_str(now()), '127.0.0.1', login_user, 'TEST_EVENT')
    assert res
