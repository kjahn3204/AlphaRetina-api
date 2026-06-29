import pytest
from dependency_injector.wiring import inject, Provide
from pytest import fixture

from app.container import ApplicationContainer
from app.conversation.model.conversation import DetailConversation
from app.conversation.repository.conversation import ConversationRepository

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
@inject
async def test_detail_conv(repository: ConversationRepository = Provide['voc.conv_repository']) -> None:
    cnv = await repository.get_cnv('1712815809.1982663')
    dc = DetailConversation.from_entity(cnv)
    print(dc)
