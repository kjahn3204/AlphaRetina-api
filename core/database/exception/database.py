from typing import Dict

from rcore.exception.base import RapidException


class DBOperationError(RapidException):
    def __init__(self, conn_name: str, e: Exception):
        self.msg = 'DB 작업 중 오류가 발생했습니다.'
        self.detail = f"connector 종류: {conn_name}, cause: {e}"


class DBConfigurationError(RapidException):
    def __init__(self, key: str, config: Dict[str, str]):
        self.msg = 'DB 설정 값이 잘못되었습니다.'
        self.detail = f"'{key}' 키가 config내에 없습니다. (config: {config})"


class NoSQLOperationError(RapidException):
    def __init__(self, conn_name: str, e: Exception):
        self.msg = f"NoSQL DB 작업 중 오류가 발생했습니다."
        self.detail = f"connector 종류: {conn_name}, cause: {e}"


class DBConnectorInitError(RapidException):
    def __init__(self, conn_name: str, e: Exception):
        self.msg = f"DB Connector 초기화 도중 오류가 발생했습니다."
        self.detail = f"connector 종류: {conn_name}, cause: {e}"


class SessionNotInitializedError(RapidException):
    def __init__(self):
        self.msg = f"Scoped session이 초기화되지 않았습니다."

