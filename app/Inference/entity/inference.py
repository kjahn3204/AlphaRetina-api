from sqlalchemy import Column, String, Integer
from core.database.entity.base import IEntity
from sqlalchemy.dialects.mysql import LONGTEXT


class SegDetailEntity(IEntity):
    __tablename__ = 'SEG_DETAIL'
    SEG_CD = Column(String(32), nullable=False, primary_key=True)  # SEG_CD -> SEGMENT_CODE
    IMG_NAME = Column(String(64), nullable=False, primary_key=True)  # IMG_NM -> IMAGE_NAME
    EXAM_HISTORY_ID = Column(String(32), nullable=False, primary_key=True)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
    AREA = Column(LONGTEXT)
    PIXEL_COUNT = Column(Integer)
