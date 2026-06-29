from typing import Any

from rcore.model.base import ModelBase
from sqlalchemy import RowMapping

from app.examination.entity.exam import ExamHistoryEntity
from datetime import datetime

from app.patient.model.patient import PatientModel


class ExamModel(ModelBase):
    exam_history_id: str  # exam_hist_id -> exam_history_id
    exam_id: str
    design_doctor_name: str  # dgsn_dctr_nm -> design_doctor_name
    title: str
    exam_dt: str  # exam_dt -> exam_date
    ai_comment: str | None = None
    doctor_comment: str | None = None  # dctr_comment -> doctor_comment
    referral_ctgr: str | None = 'O'  # referral_category -> referral_ctgr
    use_yn: str | None = 'Y'  # act_yn -> use_yn
    inference_state: str | None = 'NO_IMG'
    create_dttm: datetime | None = datetime.now()  # cre_dttm -> create_dttm

    @classmethod
    def from_entity(cls, entity: ExamHistoryEntity | None):
        if entity is None:
            return ExamModel()
        else:
            return ExamModel(
                exam_history_id=entity.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                exam_id=entity.EXAM_ID,
                design_doctor_name=entity.DESIGN_DOCTOR_NAME,  # DGSN_DCTR_NM -> DESIGN_DOCTOR_NAME
                title=entity.TITLE,
                exam_dt=entity.EXAM_DT,  # EXAM_DT -> EXAM_DATE
                ai_comment=entity.AI_COMMENT,  # AI_CMNT -> AI_COMMENT
                doctor_comment=entity.DOCTOR_COMMENT,  # DCTR_CMNT -> DOCTOR_COMMENT
                referral_ctgr=entity.REFERRAL_CTGR,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
                use_yn=entity.USE_YN,  # ACT_YN -> USE_YN
                inference_state=entity.INFERENCE_STATE,
                create_dttm=entity.CREATE_DTTM  # CRE_DTTM -> CREATE_DTTM
            )

    @classmethod
    def from_row(cls, row: RowMapping) -> 'ExamModel':
        return ExamModel(
            exam_history_id=row.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            exam_id=row.EXAM_ID,
            design_doctor_name=row.DESIGN_DOCTOR_NAME,  # DGSN_DCTR_NM -> DESIGN_DOCTOR_NAME
            title=row.TITLE,
            exam_dt=row.EXAM_DT,  # EXAM_DT -> EXAM_DATE
            ai_comment=row.AI_COMMENT,  # AI_CMNT -> AI_COMMENT
            doctor_comment=row.DOCTOR_COMMENT,  # DCTR_CMNT -> DOCTOR_COMMENT
            referral_ctgr=row.REFERRAL_CTGR,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
            use_yn=row.USE_YN,  # ACT_YN -> USE_YN
            inference_state=row.INFERENCE_STATE,
            create_dttm=row.CREATE_DTTM  # CRE_DTTM -> CREATE_DTTM
        )

    def to_entity(self) -> ExamHistoryEntity:
        return ExamHistoryEntity(
            EXAM_HISTORY_ID=self.exam_history_id,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            EXAM_ID=self.exam_id,
            DESIGN_DOCTOR_NAME=self.design_doctor_name,  # DGSN_DCTR_NM -> DESIGN_DOCTOR_NAME
            TITLE=self.title,
            EXAM_DT=self.exam_dt,  # EXAM_DT -> EXAM_DATE
            AI_COMMENT=self.ai_comment,  # AI_CMNT -> AI_COMMENT
            DOCTOR_COMMENT=self.doctor_comment,  # DCTR_CMNT -> DOCTOR_COMMENT
            REFERRAL_CTGR=self.referral_ctgr,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
            USE_YN=self.use_yn,  # ACT_YN -> USE_YN
            INFERENCE_STATE=self.inference_state,
            CREATE_DTTM=self.create_dttm  # CRE_DTTM -> CREATE_DTTM
        )


class AddExamModel(ExamModel):
    exam_history_id: str | None = None  # exam_hist_id -> exam_history_id
    design_doctor_name: str | None = None  # dgsn_dctr_nm -> design_doctor_name


class ExamWithPatient(ExamModel):
    image_count: int | None = 0
    patient: PatientModel | None = 0

    @classmethod
    def from_entity(cls, entity: ExamHistoryEntity | None):
        if entity is None:
            return ExamWithPatient()
        else:
            return ExamWithPatient(
                exam_history_id=entity.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                exam_id=entity.EXAM_ID,
                design_doctor_name=entity.DESIGN_DOCTOR_NAME,  # DGSN_DCTR_NM -> DESIGN_DOCTOR_NAME
                title=entity.TITLE,
                exam_dt=entity.EXAM_DT,  # EXAM_DT -> EXAM_DATE
                ai_comment=entity.AI_COMMENT,  # AI_CMNT -> AI_COMMENT
                doctor_comment=entity.DOCTOR_COMMENT,  # DCTR_CMNT -> DOCTOR_COMMENT
                referral_ctgr=entity.REFERRAL_CTGR,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
                use_yn=entity.USE_YN,  # ACT_YN -> USE_YN
                inference_state=entity.INFERENCE_STATE,
                create_dttm=entity.CREATE_DTTM  # CRE_DTTM -> CREATE_DTTM
            )

class ExamUpdateDC(ModelBase):
    exam_history_id: str  # exam_hist_id -> exam_history_id
    doctor_comment: str | None = ""  # dctr_comment -> doctor_comment
