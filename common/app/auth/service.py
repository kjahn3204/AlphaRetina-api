from typing import Any

from jose import JWTError, jwt, ExpiredSignatureError
from rcore.log import logger

from common.app.auth.exception import CredentialExpiredException, CredentialsException
from common.app.auth.model import TokenType, Token
from common.app.user.model import LoginUser
from common.constant import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from common.util.date import now, add_min, ts_to_dt, dt_to_str


class AuthService:
    def __init__(self, config: Any):
        self.config = config

    def _create_token(self, token_type: TokenType, to_encode: dict, expire_min: int = None) -> str:
        if token_type == TokenType.ACCESS:
            default_expire_min = self.config['accessTokenExpireMin']
            key = JWT_SECRET_KEY
        else:  # elif token_type == TokenCategory.REFRESH:
            default_expire_min = self.config['refreshTokenExpireMin']
            key = JWT_REFRESH_SECRET_KEY

        expire_min = int(default_expire_min) if expire_min is None else expire_min

        to_encode["exp"] = add_min(now(), expire_min)

        encoded_jwt = jwt.encode(to_encode, key, self.config['jwtAlgorithm'])
        return encoded_jwt

    def create_access_token(self, subject: dict, expires_delta: int = None) -> str:
        return self._create_token(TokenType.ACCESS, subject, expires_delta)

    def create_refresh_token(self, subject: dict, expires_delta: int = None) -> str:
        return self._create_token(TokenType.REFRESH, subject, expires_delta)

    def refresh_token(self, token: str) -> Token:
        payload = self._decode_token(token, TokenType.REFRESH)
        return Token(access_token=self.create_access_token(payload), refresh_token=self.create_refresh_token(payload))

    def _decode_token(self, token: str, token_type: TokenType) -> dict:
        key = JWT_SECRET_KEY if token_type == TokenType.ACCESS else JWT_REFRESH_SECRET_KEY
        algorithm = self.config['jwtAlgorithm']

        try:
            payload = jwt.decode(token, key, algorithms=[algorithm])
        except ExpiredSignatureError as e:
            raise CredentialExpiredException()
        except JWTError as e:
            raise CredentialsException(f'secret key가 일치하지 않습니다. ({e})')

        exp_dt = ts_to_dt(payload.get('exp'))
        logger.debug(f">> {payload.get('id')} - {token_type.value} token expiration time: {dt_to_str(exp_dt)}")

        return payload

    def get_auth_user_from_token(self, token: str, token_type: TokenType = TokenType.ACCESS):
        payload = self._decode_token(token, token_type)
        return LoginUser(**payload)

    def is_admin_user(self, user: LoginUser) -> bool:
        return 'ADM' in user.roles

