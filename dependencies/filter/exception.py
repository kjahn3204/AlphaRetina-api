from rcore.exception.base import RapidException


class DateEmptyError(RapidException):
    def __init__(self):
        super().__init__()
        self.msg = 'API 요청에 따른 날짜범위를 입력하지 않았습니다.'
        self.detail = f"start_dt, end_dt중 하나이상 입력해주세요"