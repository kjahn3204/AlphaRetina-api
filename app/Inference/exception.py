from fastapi import HTTPException, status


class InferenceSaveError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "추론결과를 저장하는 도중 문제가 발생하였습니다. " + (f" ({msg})" if msg is None else msg)


class AlreadyInferenceError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "이미 처리된 시험입니다. " + (f" ({msg})" if msg is None else msg)
