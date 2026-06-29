from typing import List, Dict

from dependency_injector.wiring import inject, Provide
from rcore.model.base import ModelBase
from sqlalchemy.engine import RowMapping

from common.app.code.model import Code
from common.app.code.service import CodeService
from common.app.menu.entity import MenuEntity
from common.util.collection import update_dict_keys


class MenuBase(ModelBase):
    menu_id_1: str
    menu_nm_1: str
    menu_id_2: str | None
    menu_nm_2: str | None
    menu_id_3: str | None
    menu_nm_3: str | None
    menu_tp_cd: str
    ord: int
    menu_rank: int

    @staticmethod
    def from_row(row: RowMapping):
        return MenuBase(**update_dict_keys(row, lambda k: k.lower()))

    def __getitem__(self, item):
        return super().__dict__[item]


class TreeMenu(ModelBase):
    id: str
    name: str
    order: int
    menu_type: Code | Dict | None = None
    children: List['TreeMenu'] | None = None

    @property
    def menu_type_code(self) -> str:
        return None if self.menu_type is None else self.menu_type.code

    @property
    def menu_type_name(self) -> str:
        return None if self.menu_type is None else self.menu_type.name

    @staticmethod
    @inject
    def from_entity(e: MenuEntity,
                    code_service: CodeService = Provide['common.code.service'],
                    ) -> 'TreeMenu':
        return TreeMenu(
            id=e.ID,
            name=e.NM,
            order=e.ORD,
            menu_type=code_service['MENU_TP_CD'][e.MENU_TP_CD]
        )
