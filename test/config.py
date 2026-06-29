from pytest import fixture
from rcore.config.helper import get_config
from rcore.di.wiring import autowire

from app.container import ApplicationContainer

'''
PyTest Template for Dependency Injector
2023-05-02 dhpark:
dependency injector의 ioc container를 load하여 pytest를 진행하려면 본 템플릿을 사용하세요.

'''


@fixture(scope='module', autouse=True)
def container():
    container = ApplicationContainer()
    container.init_resources()

    config = container.config()
    wire_target_list = config['core']['di']['wiring']
    wire_target_list['modules'].append(__name__)
    autowire(container, wire_target_list)

    return container


def test_get_config_helper():
    config = get_config('api.mount')
    print()
    print(config)

