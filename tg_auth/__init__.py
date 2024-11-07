from aiogram.types import User as TgUser
from aiogram.utils.web_app import WebAppUser
from x_auth.pydantic import Token as BaseToken

from tg_auth.models import User, Lang, UserStatus, AuthUser


class Token(BaseToken):
    user: AuthUser


async def user_upsert(u: TgUser | WebAppUser, status: UserStatus = None, user_model: type(User) = User) -> User:
    pic = (
        (gpp := await u.get_profile_photos(0, 1)).photos and gpp.photos[0][-1].file_unique_id
        if type(u) is TgUser
        else u.photo_url
    )  # (u.photo_url[0] if u.photo_url else None)
    user_defaults = {
        "username": u.username or u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "status": status or UserStatus.MEMBER,
        "lang": u.language_code and Lang[u.language_code],
        "pic": pic,
    }
    return (await user_model.update_or_create(user_defaults, id=u.id))[0]
