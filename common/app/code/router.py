from typing import Callable

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.requests import Request

from common.app.code.model import Code, ChgCodeType, CodeType, ChgCode
from common.app.code.service import CodeService
from common.core.fastapi.router import LoggingAPIRoute

code_router = APIRouter(prefix='/admin/codes', tags=['admin'], route_class=LoggingAPIRoute)


@code_router.get("")
@inject
async def get_codes(code_service: CodeService = Depends(Provide["common.code.service"]),
                    ):
    return await code_service.get_all()


@code_router.get("/{cd_tp_id}")
@inject
async def get_codes_by_type(cd_tp_id: str,
                            code_service: CodeService = Depends(Provide["common.code.service"]),
                            ):
    return await code_service.get_codes_by_type(cd_tp_id)


@code_router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def add_code_type(
                        background_tasks: BackgroundTasks,
                        code: CodeType,
                        code_service: CodeService = Depends(Provide["common.code.service"]),
                        cache: Callable = Depends(Provide["common.code.cache"]),
                        ):
    background_tasks.add_task(cache)
    return await code_service.add_code_type(code)


@code_router.put("/{cd_tp_id}", status_code=status.HTTP_200_OK)
@inject
async def update_code_type(
                           background_tasks: BackgroundTasks,
                           cd_tp_id: str,
                           code: ChgCodeType,
                           code_service: CodeService = Depends(Provide["common.code.service"]),
                           cache: Callable = Depends(Provide["common.code.cache"]),
                           ):
    background_tasks.add_task(cache)
    return await code_service.update_code_type(cd_tp_id, code)


@code_router.delete("/{cd_tp_id}", status_code=status.HTTP_200_OK)
@inject
async def delete_code_type(cd_tp_id: str,
                           background_tasks: BackgroundTasks,
                           code_service: CodeService = Depends(Provide["common.code.service"]),
                           cache: Callable = Depends(Provide["common.code.cache"]),
                           ):
    background_tasks.add_task(cache)
    return await code_service.delete_code_type(cd_tp_id)


@code_router.post("/{cd_tp_id}", status_code=status.HTTP_201_CREATED)
@inject
async def add_code(
                   background_tasks: BackgroundTasks,
                   cd_tp_id: str,
                   code: Code,
                   code_service: CodeService = Depends(Provide["common.code.service"]),
                   cache: Callable = Depends(Provide["common.code.cache"]),
                   ):
    background_tasks.add_task(cache)
    code.code_type = cd_tp_id
    return await code_service.add_code(code)


@code_router.put("/{cd_tp_id}/{cd}", status_code=status.HTTP_200_OK)
@inject
async def update_code(
                      background_tasks: BackgroundTasks,
                      cd_tp_id: str, cd: str, code: ChgCode,
                      code_service: CodeService = Depends(Provide["common.code.service"]),
                      cache: Callable = Depends(Provide["common.code.cache"]),
                      ):
    background_tasks.add_task(cache)
    return await code_service.update_code(cd_tp_id, cd, code)


@code_router.delete("/{cd_tp_id}/{cd}", status_code=status.HTTP_200_OK)
@inject
async def delete_code(background_tasks: BackgroundTasks,
                      cd_tp_id: str, cd: str,
                      code_service: CodeService = Depends(Provide["common.code.service"]),
                      cache: Callable = Depends(Provide["common.code.cache"]),
                      ):
    background_tasks.add_task(cache)
    return await code_service.delete_code(cd_tp_id, cd)

