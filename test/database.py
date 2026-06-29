from dependency_injector.wiring import inject, Provide
from pytest import fixture

from app.container import ApplicationContainer
from core.database.connector.rdb import AsyncMysqlConnector

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


@inject
def test_get_dbcp_status(rdb_conn: AsyncMysqlConnector = Provide['core.rdb']):
    registry = rdb_conn.session.registry.registry
    print('registry:', registry)
