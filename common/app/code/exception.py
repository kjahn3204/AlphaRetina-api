from fastapi import HTTPException, status


class CodeNotFoundError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "CodeNotFoundError" if msg is None else msg


class CodeTypeNotFoundError(HTTPException):
    def __init__(self, msg: str | None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "CodeTypeNotFoundError" if msg is None else msg


class ChannelCodeNotFoundError(CodeNotFoundError):
    def __init__(self, code):
        super().__init__(f"대화유형코드를 찾을 수 없습니다. ({code})")


class NeighborTypeCodeNotFoundError(CodeNotFoundError):
    def __init__(self, code):
        super().__init__(f"이웃유형코드를 찾을 수 없습니다. ({code})")


class SpeakerTypeCodeNotFoundError(CodeNotFoundError):
    def __init__(self, code):
        super().__init__(f"화자유형코드를 찾을 수 없습니다. ({code})")


class ComplainTypeCodeNotFoundError(CodeNotFoundError):
    def __init__(self, code):
        super().__init__(f"불만여부코드를 찾을 수 없습니다. ({code})")

