from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.requests import Request

from app.image.service import ImageService
from common.core.fastapi.router import LoggingAPIRoute

image_router = APIRouter(prefix='/image', tags=['image'], route_class=LoggingAPIRoute)


@image_router.get("/{exam_hist_id}")
@inject
async def get_images(
        exam_hist_id: str,
        page: int = 0, size: int = 50,
        image_service: ImageService = Depends(Provide['image.service']),
):
    return await image_service.get_images(page, size, exam_hist_id)


@image_router.post("/{exam_hist_id}")
@inject
async def add_images(request: Request,
                     exam_hist_id: str,
                     files: List[UploadFile] = File(...),
                     image_service: ImageService = Depends(Provide['image.service']),
                     ):
    return await image_service.add_images(exam_hist_id, files)


@image_router.delete("/{exam_hist_id}")
@inject
async def del_images(request: Request,
                     exam_hist_id: str,
                     image_service: ImageService = Depends(Provide['image.service']),
                     ):
    return await image_service.del_images(exam_hist_id)
