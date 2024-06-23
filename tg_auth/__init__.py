from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data, WebAppUser
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, AuthenticationError
from starlette.requests import HTTPConnection


class TgUser(SimpleUser):
    id: int

    def __init__(self, uid: int, username: str) -> None:
        super().__init__(username)
        self.id = uid


class TgAuth(AuthenticationBackend):
    def __init__(self, secret: str):
        self.secret: str = secret

    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, TgUser] | None:
        try:
            tg_init: str = conn.headers["Authorization"].replace('Tg ', '')
            waid: WebAppInitData = safe_parse_webapp_init_data(token=self.secret, init_data=tg_init)
            user: WebAppUser = waid.user
        except Exception as e:
            raise AuthenticationError(e)
        return AuthCredentials(), TgUser(user.id, user.username or user.first_name)
