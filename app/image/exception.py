from fastapi import HTTPException, status


class AlreadySavedImageError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "해당 시험에는 이미지가 이미 저장되어 있습니다. " + (f" ({msg})" if msg is None else msg)


class NotSupportTypeFileError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "해당 파일의 확장자는 지원하지 않습니다. " + (f" ({msg})" if msg is None else msg)
