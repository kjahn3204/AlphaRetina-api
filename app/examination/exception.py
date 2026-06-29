from fastapi import HTTPException, status


class ExamHistNotFoundError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "시험이력을 찾을 수 없습니다. " + (f" ({msg})" if msg is None else msg)
