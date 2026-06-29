from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.examination.model.exam import ExamModel, AddExamModel, ExamUpdateDC
from common.app.user.exception import AuthError
from common.core.fastapi.router import LoggingAPIRoute
from app.examination.service import ExamService
from fastapi.requests import Request

exam_router = APIRouter(prefix='/exam-hist', tags=['Exam'], route_class=LoggingAPIRoute)


@exam_router.get("/list")
@inject
async def get_exams(exam_id: str,
                    page: int = 0, size: int = 50,
                    sort: bool|None= False, sort_by: str|None='CRE_DTTM', asc: bool|None=True,
                    exam_service: ExamService = Depends(Provide['exam.service']),
                  ):
    return await exam_service.get_exams(page, size, exam_id, sort, sort_by, asc)


@exam_router.get("/{exam_hist_id}")
@inject
async def get_by_id(request: Request,
                    exam_hist_id: str,
                    exam_service: ExamService = Depends(Provide['exam.service'])
                    ):
    user_id = request.state.user.id
    return await exam_service.get_by_id(exam_hist_id, user_id)


@exam_router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def add_exam(request: Request,
                   model : AddExamModel,
                   exam_service: ExamService = Depends(Provide['exam.service'])
                   ):
    user_nm = request.state.user.name
    return await exam_service.add_exam(user_nm, model)

@exam_router.put("/update-doctor-comment", status_code=status.HTTP_200_OK)
@inject
async def update_exam(model: ExamUpdateDC,
                      exam_service: ExamService = Depends(Provide['exam.service'])):
    return await exam_service.update_exam_dc(model)


@exam_router.put("", status_code=status.HTTP_200_OK)
@inject
async def update_exam(model: ExamModel,
                      exam_service: ExamService = Depends(Provide['exam.service'])):
    return await exam_service.update_exam(model)


@exam_router.delete("/{exam_hist_id}", status_code=status.HTTP_200_OK)
@inject
async def delete_exam(exam_hist_id: str,
                      exam_service: ExamService = Depends(Provide['exam.service'])):
    return await exam_service.delete_exam(exam_hist_id)