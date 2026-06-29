from sqlalchemy import Column, String, Integer

from core.database.entity.base import EntityBase


class MenuEntity(EntityBase):
    __tablename__ = 'ADM_TBM_MENU'

    ID = Column(String(32), nullable=False, primary_key=True)
    NM = Column(String(64))
    MENU_TP_CD = Column(String(32))
    ORD = Column(Integer)
    PARENT_ID = Column(String(32))
    ACTIVE_YN = Column(String(1), default='Y', nullable=False)
