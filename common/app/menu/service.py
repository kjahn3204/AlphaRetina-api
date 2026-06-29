from collections import defaultdict
from typing import List, Callable

from common.app.code.model import CodeGroup
from common.app.code.service import CodeService
from common.app.menu.entity import MenuEntity
from common.app.menu.model import TreeMenu
from common.app.menu.repository import MenuRepository
from common.interface.repository import IRepository
from common.util.iterfuncs import fn_identity


class MenuService:
    def __init__(self,
                 repository: IRepository,
                 code_service: CodeService,
                 ) -> None:
        self._repository: MenuRepository = repository
        self.code_service: CodeService = code_service

    async def _create_tree_menu_list_model(self, src: List[MenuEntity], sort: Callable = fn_identity) -> List[TreeMenu]:
        code_group: CodeGroup = self.code_service['MENU_TP_CD']

        def _to_tree_menu(e: MenuEntity, menu_dict: defaultdict[str, List[MenuEntity]]) -> TreeMenu:
            children = None
            if e.ID in menu_dict:
                children = list(sorted(map(lambda c: _to_tree_menu(c, menu_dict), menu_dict[e.ID]), key=sort))

            tree_menu = TreeMenu.from_entity(e)
            tree_menu.children = children
            return tree_menu

        # parent_id를 key로 하는 MenuEntity 인스턴스 딕셔너리 생성
        menu_dict = defaultdict(list)
        for menu_entity in src:
            menu_dict[menu_entity.PARENT_ID].append(menu_entity)

        # 루트 메뉴(parent_id가 None인 메뉴)부터 TreeMenu 인스턴스 생성
        root_menus = []
        for menu_entity in menu_dict[None]:
            root_menus.append(_to_tree_menu(menu_entity, menu_dict))

        return sorted(root_menus, key=sort)

    async def tree(self) -> List[TreeMenu]:
        menu_entities: List[MenuEntity] = await self._repository.list()
        tree_menus = await self._create_tree_menu_list_model(menu_entities, sort=lambda m: m.order)
        return tree_menus
