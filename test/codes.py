import pytest
from dependency_injector.wiring import inject, Provide
from pytest_asyncio import fixture

from app.container import ApplicationContainer
from common.app.code.repository import CodeRepository
from core.database.aop.context import acontext


@fixture(scope='module', autouse=True)
def container():
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    return container


@pytest.mark.asyncio
@acontext
@inject
async def test_get_eternal_token(code_repository: CodeRepository = Provide['common.code.repository']):
    res = await code_repository.get_code_tree()
    print('res:', res)

