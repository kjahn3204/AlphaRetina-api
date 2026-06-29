from enum import Enum

from rcore.model.base import ModelBase


class TokenType(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class Token(ModelBase):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

