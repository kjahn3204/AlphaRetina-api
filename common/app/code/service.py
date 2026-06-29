from typing import List

from common.app.code.model import Code, CodeType, ChgCodeType, ChgCode, CodeGroup
from common.app.code.repository import CodeRepository
from common.interface.repository import IRepository
from core.database.aop.tx import transactional


class CodeService:
    def __init__(self, repository: IRepository) -> None:
        self._repository: CodeRepository = repository

    def __getitem__(self, cd_tp_id: str) -> CodeGroup:
        return next(filter(lambda g: g.id == cd_tp_id, self._repository.codes), None)

    async def get_all(self) -> List[CodeGroup]:
        return await self._repository.get_codes_by_type()

    async def get_codes_by_type(self, code_type: str) -> CodeGroup:
        code = await self._repository.get_codes_by_type(code_type)
        return code

    def get_code_values_by_type(self, code_type: str) -> List[str]:
        return list(map(lambda c: c.code, self._repository[code_type].codes))

    @transactional(conn='rdb')
    async def add_code_type(self, code: CodeType) -> bool:
        return await self._repository.add_code_type(code.to_entity())

    @transactional(conn='rdb')
    async def update_code_type(self, cd_tp_id: str, code: ChgCodeType) -> bool:
        return await self._repository.update_code_type(cd_tp_id, code.to_entity())

    @transactional(conn='rdb')
    async def delete_code_type(self, cd_tp_id: str) -> bool:
        return await self._repository.delete_code_type(cd_tp_id)

    @transactional(conn='rdb')
    async def add_code(self, code: Code) -> bool:
        return await self._repository.add_code(code.to_entity())

    @transactional(conn='rdb')
    async def update_code(self, cd_tp_id: str, cd: str, code: ChgCode) -> bool:
        return await self._repository.update_code(cd_tp_id, cd, code)

    @transactional(conn='rdb')
    async def delete_code(self, cd_tp_id: str, cd: str) -> bool:
        return await self._repository.delete_code(cd_tp_id, cd)
