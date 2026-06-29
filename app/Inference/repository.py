from typing import List

from sqlalchemy import delete
from sqlalchemy import select, and_, desc  # desc 추가

from app.Inference.entity.inference import SegDetailEntity
from app.image.entity.image import ImgDetailEntity
from core.database.repostory.sqlalchemy import SQLAlchemyRepositoryBase


class InfRepository(SQLAlchemyRepositoryBase):
    async def get_by_exam_history_id(self, exam_history_id: str) -> List[
        SegDetailEntity]:  # exam_hist_id -> exam_history_id
        stmt = select(SegDetailEntity).where(
            SegDetailEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
        async with self.session_factory() as session:
            res = await session.execute(stmt)
        return list(res.scalars().all())

    async def get_one_image_result(self, exam_history_id: str, cut_no: str) -> List[
        SegDetailEntity]:  # exam_hist_id -> exam_history_id
        stmt = (
            select(SegDetailEntity)
            .join(ImgDetailEntity, and_(
                SegDetailEntity.IMG_NAME == ImgDetailEntity.SRC_PATH,  # IMG_NM -> IMAGE_NAME
                SegDetailEntity.EXAM_HISTORY_ID == ImgDetailEntity.EXAM_HISTORY_ID))  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            .where(
                SegDetailEntity.EXAM_HISTORY_ID == exam_history_id,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                ImgDetailEntity.CUT_NO == cut_no
            )
            .order_by(desc(SegDetailEntity.PIXEL_COUNT))  # 내림차순 정렬
        )
        async with self.session_factory() as session:
            res = await session.execute(stmt)
        return list(res.scalars().all())

    async def add_segs(self, entities: List[SegDetailEntity]):  # SegDetailEntity 추가
        async with self.session_factory() as session:
            session.add_all(entities)
            await session.commit()
        return True

    async def del_segs(self, exam_history_id: str):  # exam_hist_id -> exam_history_id
        stmt = delete(SegDetailEntity).where(
            SegDetailEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
        async with self.session_factory() as session:
            await session.execute(stmt)
            await session.commit()
        return True
