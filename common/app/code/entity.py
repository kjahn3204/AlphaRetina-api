from sqlalchemy import Column, String

from core.database.entity.base import IEntity


class CodeTypeEntity(IEntity):
    __tablename__ = 'CODE_TP'

    CD_TP_ID = Column(String(32), nullable=False, primary_key=True)
    NAME = Column(String(64))  # 수정: NM -> NAME
    ADD_INFO = Column(String(32))


class CodeEntity(IEntity):
    __tablename__ = 'CODE'

    CD = Column(String(32), nullable=False, primary_key=True)
    CD_TP_ID = Column(String(32), nullable=False, primary_key=True)
    NAME = Column(String(64))  # 수정: NM -> NAME
    ADD_INFO = Column(String(32))
