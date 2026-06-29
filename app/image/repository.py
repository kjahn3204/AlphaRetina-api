from typing import List

from sqlalchemy import delete, select, update

from app.Inference.entity.inference import SegDetailEntity
from app.examination.entity.exam import ExamHistoryEntity
from app.image.entity.image import ImgDetailEntity
# from app.patient.entity.patient import PatientEntity
from core.database.repostory.sqlalchemy import SQLAlchemyRepositoryBase


class ImageRepository(SQLAlchemyRepositoryBase):
    async def get_by_exam_history_id(self, exam_history_id: str) -> List[
        ImgDetailEntity]:  # exam_hist_id -> exam_history_id
        stmt = select(ImgDetailEntity).where(
            ImgDetailEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
        async with self.session_factory() as session:
            res = await session.execute(stmt)
        return list(res.scalars().all())

    async def add_images(self, entities: List[ImgDetailEntity]):
        async with self.session_factory() as session:
            session.add_all(entities)
            await session.commit()
        return True

    async def del_images(self, exam_history_id: str):  # exam_hist_id -> exam_history_id
        async with self.session_factory() as session:
            stmt = delete(ImgDetailEntity).where(
                ImgDetailEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            await session.execute(stmt)

            seg_stmt = delete(SegDetailEntity).where(
                SegDetailEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            await session.execute(seg_stmt)

            await session.commit()
        return True

    async def update_exam_inf_state(self, exam_history_id: str, inf_state: str):  # exam_hist_id -> exam_history_id
        async with self.session_factory() as session:
            stmt = select(ExamHistoryEntity).where(
                ExamHistoryEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            res = await session.execute(stmt)
            customer = res.scalar_one_or_none()

            if customer is None:
                return False  # 또는 적절한 예외를 발생시킬 수 있습니다.

            customer.INFERENCE_STATE = inf_state  # INF_YN -> INFERENCE_YN
            session.add(customer)  # 변경 사항을 세션에 추가
            await session.commit()  # 변경 사항을 커밋
        return True

    async def get_by_page(self, skip: int, limit: int, exam_history_id: str) -> List[
        ImgDetailEntity]:  # exam_hist_id -> exam_history_id
        async with self.session_factory() as session:
            stmt = select(ImgDetailEntity).where(ImgDetailEntity.EXAM_HISTORY_ID == exam_history_id).offset(skip).limit(
                limit)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            res = await session.execute(stmt)
            return list(res.scalars().all())

    async def update_images(self, entities: List[ImgDetailEntity]):
        async with self.session_factory() as session:
            for entity in entities:
                stmt = update(ImgDetailEntity).where(
                    ImgDetailEntity.CUT_NO == entity.CUT_NO,
                    ImgDetailEntity.EXAM_HISTORY_ID == entity.EXAM_HISTORY_ID  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                ).values(**entity.to_dict(exclude_none=True))
                await session.execute(stmt)
            await session.commit()
        return True
