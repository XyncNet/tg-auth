from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data, WebAppUser
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError
from starlette.requests import HTTPConnection
from x_auth.pydantic import AuthUser


class TgAuthBack(AuthenticationBackend):
    def __init__(self, secret: str):
        self.secret: str = secret

    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, AuthUser] | None:
        try:
            tg_init: str = conn.headers["Authorization"].replace('Tg ', '')
            waid: WebAppInitData = safe_parse_webapp_init_data(token=self.secret, init_data=tg_init)
            user: WebAppUser = waid.user
        except Exception as e:
            raise AuthenticationError(e)
        return AuthCredentials(), AuthUser(id=user.id, username=user.username or user.first_name)
