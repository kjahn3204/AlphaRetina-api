from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from common.app.menu.model import TreeMenu
from common.app.menu.service import MenuService
from common.core.fastapi.router import LoggingAPIRoute

menu_router = APIRouter(prefix='/admin/menu', tags=['admin'], route_class=LoggingAPIRoute)


@menu_router.get("")
@inject
async def list(menu_service: MenuService = Depends(Provide['common.menu.service'])
               ) -> List[TreeMenu]:
    return await menu_service.tree()
