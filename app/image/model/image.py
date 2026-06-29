from pydantic import computed_field
from rcore.model.base import ModelBase
from sqlalchemy import RowMapping

from app.image.entity.image import ImgDetailEntity


class ImgDetailModel(ModelBase):
    exam_history_id: str  # exam_hist_id -> exam_history_id
    cut_no: int
    img_name: str  # img_nm -> image_name
    referral_ctgr: str | None = 'O'  # referral_category -> referral_ctgr
    img_set_len: int | None = None  # img_set_len -> image_set_length
    width: int | None = None
    height: int | None = None
    src_path: str | None = None  # src_path -> source_path

    @computed_field
    def api_path(self) -> str | None:
        return f"/data/{self.src_path}"  # src_path -> source_path

    @classmethod
    def from_entity(cls, entity: ImgDetailEntity | None):
        if entity is None:
            return ImgDetailModel()
        else:
            return ImgDetailModel(
                img_name=entity.IMG_NAME,  # IMG_NM -> IMAGE_NAME
                exam_history_id=entity.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                referral_ctgr=entity.REFERRAL_CTGR,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
                img_set_len=entity.IMG_SET_LEN,  # IMG_SET_LEN -> IMAGE_SET_LENGTH
                cut_no=entity.CUT_NO,
                width=entity.WIDTH,
                height=entity.HEIGHT,
                src_path=entity.SRC_PATH  # SRC_PATH -> SOURCE_PATH
            )

    @classmethod
    def from_row(cls, row: RowMapping) -> 'ImgDetailModel':
        return ImgDetailModel(
            img_name=row.IMG_NAME,  # IMG_NM -> IMAGE_NAME
            exam_history_id=row.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            referral_ctgr=row.REFERRAL_CTGR,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
            img_set_len=row.IMG_SET_LEN,  # IMG_SET_LEN -> IMAGE_SET_LENGTH
            cut_no=row.CUT_NO,
            width=row.WIDTH,
            height=row.HEIGHT,
            src_path=row.SRC_PATH  # SRC_PATH -> SOURCE_PATH
        )

    def to_entity(self) -> ImgDetailEntity:
        return ImgDetailEntity(
            IMG_NAME=self.img_name,  # IMG_NM -> IMAGE_NAME
            EXAM_HISTORY_ID=self.exam_history_id,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            REFERRAL_CTGR=self.referral_ctgr,  # REFERRAL_CATEGORY -> REFERRAL_CTGR
            IMG_SET_LEN=self.img_set_len,  # IMG_SET_LEN -> IMAGE_SET_LENGTH
            CUT_NO=self.cut_no,
            WIDTH=self.width,
            HEIGHT=self.height,
            SRC_PATH=self.src_path  # SRC_PATH -> SOURCE_PATH
        )
