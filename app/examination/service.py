from typing import List

import shortuuid

from app.examination.entity.exam import ExamHistoryEntity
from app.examination.exception import ExamHistNotFoundError
from app.examination.model.exam import ExamModel, ExamWithPatient, ExamWithPatient, ExamUpdateDC
from app.examination.repository import ExamRepository
from app.image.model.image import ImgDetailModel
from app.image.repository import ImageRepository


class ExamService:
    def __init__(self, repository: ExamRepository, image_repository: ImageRepository):
        self._repo: ExamRepository = repository
        self._image_repository: ImageRepository = image_repository

    async def get_exams(self, page: int, size: int, exam_id: str, sort: bool, sort_by: str, asc: bool) -> List[
        ExamHistoryEntity]:
        return await self._repo.get_by_page(page, size, exam_id, sort, sort_by, asc)

    async def get_by_id(self, exam_history_id: str, user_id:str) -> ExamWithPatient:  # exam_hist_id -> exam_history_id
        e = await self._repo.get_by_id(exam_history_id)  # exam_hist_id -> exam_history_id
        p = await self._repo.get_patient_by_exam_hist_id(exam_history_id,user_id)

        if e is None:
            raise ExamHistNotFoundError(f"exam_history_id : {exam_history_id}")  # exam_hist_id -> exam_history_id

        exam_hist = ExamWithPatient.from_entity(e)

        image_entities = await self._image_repository.get_by_exam_history_id(
            exam_history_id)  # exam_hist_id -> exam_history_id
        image = list(map(ImgDetailModel.from_entity, image_entities))
        exam_hist.image_count = len(image)
        exam_hist.patient = p
        return exam_hist

    async def add_exam(self, user_nm: str, model: ExamModel):
        exam_history_id = shortuuid.ShortUUID().random(length=32)  # exam_hist_id -> exam_history_id
        model.exam_history_id = exam_history_id  # exam_hist_id -> exam_history_id
        model.design_doctor_name = user_nm  # dgsn_dctr_nm -> design_doctor_name
        entity = model.to_entity()
        if await self._repo.add_exam_history(entity):
            return {"exam_history_id": exam_history_id}  # exam_hist_id -> exam_history_id

    async def update_exam(self, model: ExamModel):
        entity = model.to_entity()
        return await self._repo.update_exam(entity)

    async def update_exam_dc(self, model: ExamUpdateDC):
        return await self._repo.update_exam_dc(model.exam_history_id, model.doctor_comment)


    async def delete_exam(self, exam_history_id: str):  # exam_hist_id -> exam_history_id
        return await self._repo.delete_exam(exam_history_id)  # exam_hist_id -> exam_history_id