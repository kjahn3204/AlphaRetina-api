from typing import Any

from rcore.exception.base import RapidException


class CredentialsException(RapidException):
    def __init__(self, detail: str, extra: Any = None):
        super().__init__("인증 정보를 확인할 수 없습니다.", detail, extra)


class CredentialExpiredException(CredentialsException):
    def __init__(self, extra: Any = None):
        super().__init__("인증 정보가 만료되었습니다.", extra)
