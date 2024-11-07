from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data, WebAppUser
from starlette.authentication import AuthCredentials
from starlette.requests import HTTPConnection
from x_auth import AuthException, AuthFailReason
from x_auth.backend import AuthBackend

from tg_auth.models import AuthUser


class TgAuthBack(AuthBackend):
    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, AuthUser] | None:
        if not (tg_init := await self.auth_scheme(conn)):
            raise AuthException(AuthFailReason.header, "No Tg initData in Authorization header")
        try:
            waid: WebAppInitData = safe_parse_webapp_init_data(token=self.secret, init_data=tg_init)
            user: WebAppUser = waid.user
        except Exception as e:
            raise AuthException(AuthFailReason.header, e)
        return AuthCredentials(), AuthUser(id=user.id, username=user.username or user.first_name)
