from typing import List

from sqlalchemy import insert, delete, select, update

from app.Inference.entity.inference import SegDetailEntity
from app.examination.entity.exam import ExamHistoryEntity, ExamEntity
from app.examination.model.exam import ExamModel
from app.image.entity.image import ImgDetailEntity
from app.patient.model.patient import PatientModel
from core.database.repostory.sqlalchemy import SQLAlchemyRepositoryBase


class ExamRepository(SQLAlchemyRepositoryBase):
    # async def get_by_page(self, skip: int, limit: int, exam_id: str) -> List[ExamHistoryEntity]:
    #     stmt = select(ExamHistoryEntity).where(ExamHistoryEntity.EXAM_ID == exam_id).offset(skip).limit(limit)
    #     res = await self.session.execute(stmt)
    #     return list(res.scalars().all())

    async def get_by_page(self, page: int, size: int, exam_id: str, sort: bool, sort_by: str, asc: bool) -> List[
        ExamHistoryEntity]:
        sort_query = f'''ORDER BY {sort_by} {'ASC' if asc else 'DESC'}''' if sort else ''

        query = f'''
                            SELECT *
                            FROM EXAM_HIST H
                            WHERE EXAM_ID = '{exam_id}' AND USE_YN = 'Y'
                            {sort_query}
                        '''  # ACT_YN -> USE_YN
        return await self.execute_sql(query, mapper=ExamModel.from_row, pagination=True, page=page, size=size)

    async def get_by_id(self, exam_history_id: str) -> ExamHistoryEntity | None:  # exam_hist_id -> exam_history_id
        async with self.session_factory() as session:
            stmt = select(ExamHistoryEntity).where(
                ExamHistoryEntity.EXAM_HISTORY_ID == exam_history_id,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                ExamHistoryEntity.USE_YN == 'Y'  # ACT_YN -> USE_YN
            )
            res = await session.execute(stmt)
            customer = res.scalar_one_or_none()
        return customer

    async def find_list_by_name(self, customer_nm: str, user_id: str) -> List[ExamHistoryEntity]:
        async with self.session_factory() as session:
            stmt = select(ExamHistoryEntity).where(
                ExamHistoryEntity.NM.like(f'%{customer_nm}%'),
                ExamHistoryEntity.USER_ID == user_id
            )
            res = await session.execute(stmt)
            customer = list(res.scalars().all())
        return customer

    async def add_exam_history(self, entity: ExamHistoryEntity):
        async with self.session_factory() as session:
            stmt = insert(ExamHistoryEntity).values(**entity.to_dict())
            await session.execute(stmt)
            await session.commit()
        return True

    async def add_exam(self, entity: ExamEntity):
        async with self.session_factory() as session:
            stmt = insert(ExamEntity).values(**entity.to_dict())
            await session.execute(stmt)
            await session.commit()
        return True

    async def update_exam(self, entity: ExamHistoryEntity):
        async with self.session_factory() as session:
            stmt = (
                update(ExamHistoryEntity)
                .where(ExamHistoryEntity.EXAM_HISTORY_ID == entity.EXAM_HISTORY_ID)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                .values(**entity.to_dict(exclude_none=True))
            )
            await session.execute(stmt)
            await session.commit()
        return True

    async def update_exam_dc(self, exam_history_id: str, doctor_comment:str):
        async with self.session_factory() as session:
            stmt = (
                update(ExamHistoryEntity)
                .where(ExamHistoryEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                .values(DOCTOR_COMMENT=doctor_comment)
            )
            await session.execute(stmt)
            await session.commit()
        return True

    async def update_exam_referral_ctgr(self, exam_history_id: str, referral_ctgr: str):
        async with self.session_factory() as session:
            stmt = (
                update(ExamHistoryEntity)
                .where(ExamHistoryEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                .values(REFERRAL_CTGR=referral_ctgr)
            )
            await session.execute(stmt)
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

    async def delete_exam(self, exam_history_id: str):  # exam_hist_id -> exam_history_id
        async with self.session_factory() as session:
            stmt = select(ExamHistoryEntity).where(
                ExamHistoryEntity.EXAM_HISTORY_ID == exam_history_id)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            res = await session.execute(stmt)
            customer = res.scalar_one_or_none()

            if customer is None:
                return False  # 또는 적절한 예외를 발생시킬 수 있습니다.

            customer.USE_YN = 'N'  # ACT_YN -> USE_YN
            session.add(customer)  # 변경 사항을 세션에 추가
            await session.commit()  # 변경 사항을 커밋

            # stmt = delete(ExamHistoryEntity).where(ExamHistoryEntity.EXAM_HIST_ID == exam_hist_id)
            # await session.execute(stmt)

            # image_stmt = delete(ImgDetailEntity).where(ImgDetailEntity.EXAM_HIST_ID == exam_hist_id)
            # await session.execute(image_stmt)
            #
            # seg_stmt = delete(SegDetailEntity).where(SegDetailEntity.EXAM_HIST_ID == exam_hist_id)
            # await session.execute(seg_stmt)

            await session.commit()
        return True


    async def get_patient_by_exam_hist_id(self, exam_hist_id: str, user_id: str):
        query = f'''
                    SELECT P.*
                    FROM PATIENT P
                        INNER JOIN EXAM E ON E.PATIENT_ID = P.ID  
                        INNER JOIN EXAM_HIST H ON H.EXAM_ID = E.EXAM_ID 
                    WHERE H.EXAM_HISTORY_ID = '{exam_hist_id}' AND E.USER_ID = '{user_id}' AND E.USE_YN = 'Y'
                    LIMIT 1
        '''
        return await self.execute_sql(query, mapper=PatientModel.from_row, get_one=True)
