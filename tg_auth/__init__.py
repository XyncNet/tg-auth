from aiogram.types import User as TgUser
from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data, WebAppUser
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, AuthenticationError
from starlette.requests import HTTPConnection

from tg_auth.models import UserStatus, User, Lang


async def user_upsert(u: TgUser | WebAppUser, status: UserStatus = None) -> (User, bool):
    pic = (gpp := await u.get_profile_photos(0, 1)).photos and gpp.photos[0][-1].file_unique_id if type(u) is TgUser else u.photo_url  # (u.photo_url[0] if u.photo_url else None)
    user_defaults = {
        'username': u.username or u.id,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'status': status or UserStatus.MEMBER,
        'lang': u.language_code and Lang[u.language_code],
        'pic': pic
    }
    return await User.update_or_create(user_defaults, id=u.id)


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
