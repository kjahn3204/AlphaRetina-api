from typing import List
from rcore.log import logger
from sqlalchemy import func, insert, delete, select, update
from common.app.code.entity import CodeTypeEntity, CodeEntity
from common.app.code.exception import CodeTypeNotFoundError, CodeNotFoundError
from common.app.code.model import CodeGroup, Code, ChgCode
from common.util.iterfuncs import groupby_mapper
from core.database.repostory.sqlalchemy import SQLAlchemyRepositoryBase


class CodeRepository(SQLAlchemyRepositoryBase):
    __cached_codes: List[CodeGroup]

    def __getitem__(self, cd_tp_id: str) -> CodeGroup:
        return next(filter(lambda g: g.id == cd_tp_id, self.__cached_codes), None)

    @property
    def codes(self):
        return self.__cached_codes

    async def cache(self):
        logger.info(f'Caching codes for {self.__class__.__name__}')
        self.__cached_codes = await self.get_codes_by_type()

    async def get_codes_by_type(self, cd_tp_id: str | None = None) -> List[CodeGroup] | CodeGroup | None:
        filter_cd_tp_id = f"AND T.CD_TP_ID = '{cd_tp_id}'" if cd_tp_id is not None else ''
        res = await self.execute_sql(f'''
            SELECT T.CD_TP_ID AS CD_TP_ID
                 , T.NAME AS CD_TP_NAME   
                 , C.CD
                 , C.NAME                 
                 , C.ADD_INFO
              FROM CODE_TP T
              INNER JOIN CODE C ON T.CD_TP_ID = C.CD_TP_ID
               {filter_cd_tp_id}
        ''')
        if len(res) > 0:
            result: List[CodeGroup] = groupby_mapper(
                res, to_list=True,
                key=lambda r: r.CD_TP_ID,
                key_mapper=CodeGroup.from_row,
                value_mapper=Code.from_row,
                list_item_mapper=lambda k, v: CodeGroup(
                    id=k.id,
                    name=k.name,  # 여기 사용되는 name은 `.from_row()` 결과가 반영되므로 NAME으로 자동 매핑됨
                    codes=v
                )
            )
            return result if len(result) > 1 else result[0]
        else:
            return None

    async def add_code_type(self, entity: CodeTypeEntity) -> bool:
        async with self.session_factory() as session:
            stmt = insert(CodeTypeEntity).values(
                **entity.to_dict(),
            )
            await session.execute(stmt)
        return True

    async def update_code_type(self, cd_tp_id: str, entity: CodeTypeEntity) -> bool:
        async with self.session_factory() as session:
            stmt = update(CodeTypeEntity).where(CodeTypeEntity.CD_TP_ID == cd_tp_id).values(
                **entity.to_dict(exclude_none=True)
            )
            res = await session.execute(stmt)
        return True

    async def delete_code_type(self, cd_tp_id: str) -> bool:
        async with self.session_factory() as session:
            stmt = select(CodeTypeEntity).where(CodeTypeEntity.CD_TP_ID == cd_tp_id)
            res = await session.execute(stmt)
            code_type: CodeTypeEntity = res.scalar_one_or_none()
            if not code_type:
                raise CodeTypeNotFoundError(f"CodeTypeNotFoundError : {cd_tp_id}")
            stmt = delete(CodeTypeEntity).where(CodeTypeEntity.CD_TP_ID == cd_tp_id)
            res = await session.execute(stmt)
        return True

    async def add_code(self, entity: CodeEntity):
        async with self.session_factory() as session:
            stmt = insert(CodeEntity).values(
                **entity.to_dict()
            )
            await session.execute(stmt)
        return True

    async def update_code(self, cd_tp_id: str, cd: str, cum: ChgCode):
        async with self.session_factory() as session:
            entity = cum.to_entity()
            stmt = update(CodeEntity).where(
                CodeEntity.CD_TP_ID == cd_tp_id,
                CodeEntity.CD == cd
            ).values(
                **entity.to_dict(exclude_none=True)
            )
            res = await session.execute(stmt)
        return True

    async def delete_code(self, cd_tp_id: str, cd: str) -> bool:
        async with self.session_factory() as session:
            stmt = select(CodeTypeEntity).where(CodeTypeEntity.CD_TP_ID == cd_tp_id)
            res = await session.execute(stmt)
            code_type: CodeTypeEntity = res.scalar_one_or_none()
            if not code_type:
                raise CodeTypeNotFoundError(f"CodeTypeNotFoundError : {cd_tp_id}")
            stmt = select(CodeEntity).where(
                CodeEntity.CD_TP_ID == cd_tp_id,
                CodeEntity.CD == cd)
            res = await session.execute(stmt)
            code: CodeEntity = res.scalar_one_or_none()
            if not code:
                raise CodeNotFoundError(f"CodeNotFoundError : {cd}")
            stmt = delete(CodeEntity).where(
                CodeEntity.CD_TP_ID == cd_tp_id,
                CodeEntity.CD == cd
            )
            res = await session.execute(stmt)
        return True
