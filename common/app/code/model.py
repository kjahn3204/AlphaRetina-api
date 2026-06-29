from typing import List

from rcore.aop.serdes import json_ignore
from rcore.model.base import ModelBase
from sqlalchemy import RowMapping

from common.app.code.entity import CodeEntity, CodeTypeEntity


@json_ignore(props={'code_type', 'code_type_name', 'is_active'}, none=True)
class Code(ModelBase):
    code_type: str | None = None
    code_type_name: str | None = None
    code: str | None = None
    name: str | None = None
    add_info: str | None = None
    children: List['Code'] | None = None

    def __str__(self):
        return f'{self.code}[{self.name}]'

    @staticmethod
    def from_row(r: RowMapping):
        if r.CD is None:
            return None
        else:
            return Code(
                code_type=r.CD_TP_ID,
                code_type_name=r.CD_TP_NAME,  # 수정된 컬럼
                code=r.CD,
                name=r.NAME,  # 수정된 컬럼
                add_info=r.ADD_INFO
            )

    def to_entity(self) -> CodeEntity:
        return CodeEntity(
            CD_TP_ID=self.code_type,
            CD=self.code,
            NAME=self.name,  # 수정된 컬럼
            ADD_INFO=self.add_info
        )


@json_ignore(props={
    'codes': {
        "__all__": {'code_type', 'code_type_name', 'is_active'}
    },
    'is_active': ...
}, none=True)
class CodeGroup(ModelBase):
    id: str
    name: str | None = None
    codes: List[Code] | None = None

    def __getitem__(self, code: str) -> Code:
        return next(filter(lambda c: c.code == code, self.codes), None)

    @staticmethod
    def from_row(r: RowMapping):
        return CodeGroup(
            id=r.CD_TP_ID,
            name=r.CD_TP_NAME  # 수정된 컬럼
        )


class ChgCode(ModelBase):
    code_type: str | None = None
    code: str | None = None
    name: str | None = None
    add_info: str | None = None

    def to_entity(self):
        return CodeEntity(
            CD_TP_ID=self.code_type,
            CD=self.code,
            NAME=self.name,  # 수정된 컬럼
            ADD_INFO=self.add_info
        )


class CodeType(ModelBase):
    id: str
    name: str
    add_info: str | None = None

    def __str__(self):
        return f'{self.id}'

    def to_entity(self) -> CodeTypeEntity:
        return CodeTypeEntity(
            CD_TP_ID=self.id,
            NAME=self.name,  # 수정된 컬럼
            ADD_INFO=self.add_info
        )


class ChgCodeType(ModelBase):
    code_type: str | None = None
    name: str | None = None
    add_info: str | None = None

    def to_entity(self) -> CodeTypeEntity:
        return CodeTypeEntity(
            CD_TP_ID=self.code_type,
            NAME=self.name,  # 수정된 컬럼
            ADD_INFO=self.add_info
        )
