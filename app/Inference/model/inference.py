import ast  # 문자열을 안전하게 파싱하기 위한 ast 모듈 추가

from rcore.model.base import ModelBase
from sqlalchemy import RowMapping

from app.Inference.entity.inference import SegDetailEntity


class SegDetailModel(ModelBase):
    seg_code: str  # seg_cd -> segment_code
    img_name: str  # img_nm -> image_name
    exam_history_id: str  # exam_hist_id -> exam_history_id
    area: list
    pixel_count: int | None = 0

    @classmethod
    def from_entity(cls, entity: SegDetailEntity | None) -> 'SegDetailModel':
        if entity is None:
            return SegDetailModel()
        else:
            area_list = []
            if entity.AREA:
                area_items = entity.AREA.split('|')
                for item in area_items:
                    type_, path = item.split(':')
                    path_list = ast.literal_eval(path)
                    area_list.append({"type": type_, "path": path_list})

            return SegDetailModel(
                seg_code=entity.SEG_CD,  # SEG_CD -> SEGMENT_CODE
                img_name=entity.IMG_NAME,  # IMG_NM -> IMAGE_NAME
                exam_history_id=entity.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                area=area_list,
                pixel_count=entity.PIXEL_COUNT
            )

    @classmethod
    def from_row(cls, row: RowMapping) -> 'SegDetailModel':
        area_list = []
        if row.AREA:
            area_items = row.AREA.split('|')
            for item in area_items:
                type_, path = item.split(':')
                path_list = ast.literal_eval(path)
                area_list.append({"type": type_, "path": path_list})

        return SegDetailModel(
            seg_code=row.SEG_CD,  # SEG_CD -> SEGMENT_CODE
            img_name=row.IMG_NAME,  # IMG_NM -> IMAGE_NAME
            exam_history_id=row.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            area=area_list,
            pixel_count=row.PIXEL_COUNT
        )

    def to_entity(self) -> SegDetailEntity:
        area_str = ''
        if self.area:
            area_items = []
            for area in self.area:
                path_str = repr(area["path"])  # 리스트를 문자열로 변환
                area_items.append(f'{area["type"]}:{path_str}')
            area_str = '|'.join(area_items)

        return SegDetailEntity(
            SEG_CD=self.seg_code,  # SEG_CD -> SEGMENT_CODE
            IMG_NAME=self.img_name,  # IMG_NM -> IMAGE_NAME
            EXAM_HISTORY_ID=self.exam_history_id,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
            AREA=area_str,
            PIXEL_COUNT=self.pixel_count
        )


class SegDetailModelAddNm(SegDetailModel):
    seg_name: str | None = None  # seg_nm -> segment_name

    @classmethod
    def from_entity(cls, entity: SegDetailEntity | None) -> 'SegDetailModelAddNm':
        if entity is None:
            return SegDetailModelAddNm()
        else:
            area_list = []
            if entity.AREA:
                area_items = entity.AREA.split('|')
                for item in area_items:
                    type_, path = item.split(':')
                    path_list = ast.literal_eval(path)
                    area_list.append({"type": type_, "path": path_list})

            return SegDetailModelAddNm(
                seg_code=entity.SEG_CD,  # SEG_CD -> SEGMENT_CODE
                img_name=entity.IMG_NAME,  # IMG_NM -> IMAGE_NAME
                exam_history_id=entity.EXAM_HISTORY_ID,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                area=area_list,
                pixel_count=entity.PIXEL_COUNT
            )
