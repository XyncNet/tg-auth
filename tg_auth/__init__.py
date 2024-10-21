from datetime import timedelta
from aiogram.types import User as TgUser
from aiogram.utils.web_app import WebAppUser
from x_auth import jwt_encode
from x_auth.pydantic import Token, AuthUser

from tg_auth.models import UserStatus, User, Lang


async def user_upsert(u: TgUser | WebAppUser, status: UserStatus = None, user_model: type(User) = User) -> User:
    pic = (gpp := await u.get_profile_photos(0, 1)).photos and gpp.photos[0][-1].file_unique_id if type(u) is TgUser else u.photo_url  # (u.photo_url[0] if u.photo_url else None)
    user_defaults = {
        'username': u.username or u.id,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'status': status or UserStatus.MEMBER,
        'lang': u.language_code and Lang[u.language_code],
        'pic': pic
    }
    return (await user_model.update_or_create(user_defaults, id=u.id))[0]


async def _twa2tok(twa_user: WebAppUser, bot_token: str, expire: timedelta) -> Token:  # _common
    db_user: User = await user_upsert(twa_user)
    auth_user: AuthUser = db_user.get_auth()
    access_token = jwt_encode(auth_user, bot_token, expire)
    return Token(access_token=access_token, user=auth_user)
