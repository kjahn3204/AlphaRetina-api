from sqlalchemy import Column, String, Text, CHAR
from sqlalchemy import DateTime

from core.database.entity.base import IEntity


class ExamHistoryEntity(IEntity):
    __tablename__ = 'EXAM_HIST'

    EXAM_ID = Column(String(32), nullable=False)  # 변경되지 않음
    EXAM_HISTORY_ID = Column(String(32), nullable=False, primary_key=True)  # EXAM_HIST_ID -> EXAM_HISTORY_ID
    DESIGN_DOCTOR_NAME = Column(String(24), nullable=False)  # DGSN_DCTR_NM -> DESIGN_DOCTOR_NAME
    TITLE = Column(String(64), nullable=False)  # 변경되지 않음
    EXAM_DT = Column(CHAR(8), nullable=False)
    AI_COMMENT = Column(Text, nullable=True)  # AI_CMNT -> AI_COMMENT
    DOCTOR_COMMENT = Column(Text, nullable=True)  # DCTR_CMNT -> DOCTOR_COMMENT
    REFERRAL_CTGR = Column(String(3), nullable=False)  # REFERRAL_CATEGORY -> REFERRAL_CTGR
    USE_YN = Column(String(1), nullable=False)  # ACT_YN -> USE_YN
    INFERENCE_STATE = Column(String(15), default='NO_IMG')
    CREATE_DTTM = Column(DateTime, nullable=False)  # CRE_DTTM -> CREATE_DTTM


class ExamEntity(IEntity):
    __tablename__ = 'EXAM'

    EXAM_ID = Column(String(32), nullable=False, primary_key=True)  # 변경되지 않음
    USER_ID = Column(String(64), nullable=False, primary_key=True)  # 변경되지 않음
    PATIENT_ID = Column(String(32), nullable=False, primary_key=True)  # PA_ID -> PATIENT_ID
    MASTER_YN = Column(String(1), nullable=False)  # MSTR_YN -> MASTER_YN
    USE_YN = Column(String(1), nullable=False)  # ACT_YN -> USE_YN
