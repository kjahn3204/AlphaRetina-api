from sqlalchemy import Column, String, Integer
from core.database.entity.base import IEntity


class ImgDetailEntity(IEntity):
    __tablename__ = 'IMG_DETAIL'
    EXAM_HISTORY_ID = Column(String(32), nullable=False, primary_key=True)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
    CUT_NO = Column(Integer, nullable=False, primary_key=True)
    IMG_NAME = Column(String(64), nullable=False)  # IMG_NM -> IMAGE_NAME
    REFERRAL_CTGR = Column(String(3), default='O')  # REFERRAL_CATEGORY -> REFERRAL_CTGR
    IMG_SET_LEN = Column(Integer)  # IMG_SET_LEN -> IMAGE_SET_LENGTH
    WIDTH = Column(Integer)
    HEIGHT = Column(Integer)
    SRC_PATH = Column(String(256), nullable=False)  # SRC_PATH -> SOURCE_PATH
