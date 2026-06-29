from datetime import datetime

from pytest_asyncio import fixture
from rcore.aop.serdes import json_ignore
from rcore.model.base import ModelBase

from app.container import ApplicationContainer


@fixture(scope='module', autouse=True)
def container():
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    return container


def test_json_ignore_dict_none():
    @json_ignore(props={'created'}, none=True)
    class Department(ModelBase):
        id: str
        name: str
        location: str
        created: datetime | None = None
        changed: datetime | None = None

    dept = Department(id='d1', name='department 01', location='Manhattan, NYC')
    d = {'id': 'd1', 'name': 'department 01', 'location': 'Manhattan, NYC'}
    assert dept.dict() == d


def test_json_ignore_dict_2():
    @json_ignore(props={'created'}, none=True)
    class Department(ModelBase):
        id: str
        name: str
        location: str
        created: datetime
        changed: datetime | None = None

    @json_ignore(props={
        'id': ...,
        'dept': {'id', 'created', 'changed'},
        'changed': ...,
    }, none=True)
    class Person(ModelBase):
        id: str
        name: str
        age: int
        dept: Department
        created: datetime
        changed: datetime | None = None

    dept = Department(id='d1', name='department 01', location='Manhattan, NYC', created=datetime(2024, 1, 1))
    person = Person(id='p1', name='jake', age=20, dept=dept, created=datetime(2024, 1, 1))
    assert person.json() == '{"name":"jake","age":20,"dept":{"name":"department 01","location":"Manhattan, NYC"},"created":"2024-01-01T00:00:00"}'


def test_json_ignore_json():
    @json_ignore(props={'nm'}, none=True)
    class TestCode(ModelBase):
        cd: str
        nm: str
        ext: str | None

    c = TestCode(cd='t1', nm='test', ext=None)
    assert c.json() == '{"cd":"t1"}'

