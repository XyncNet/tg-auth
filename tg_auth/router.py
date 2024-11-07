from datetime import timedelta

from fastapi.responses import JSONResponse
from aiogram.utils.auth_widget import check_signature
from aiogram.utils.web_app import WebAppUser, WebAppInitData, safe_parse_webapp_init_data
from pydantic import BaseModel
from tortoise import ConfigurationError

from tg_auth.models import AuthUser

# from tg_auth.backend import TgAuthBack
from x_auth import AuthException, AuthFailReason, jwt_encode  # , BearerSecurity, BearerModel
from x_auth.router import AuthRouter

from tg_auth import User, Token, user_upsert


class TgData(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class TgRouter(AuthRouter):
    def __init__(self, secret: str, db_user_model: type(User) = User):
        # scheme = BearerSecurity(BearerModel(scheme='tg'))
        super().__init__(secret, db_user_model)  # , TgAuthBack(secret, scheme), scheme)

        # api refresh token
        # todo: can't inherit from parent because method in __init__ func
        async def refresh(auth_user: AuthUser = self.depend.AUTHENTICATED) -> Token:
            try:
                db_user: User = await self.db_user_model[auth_user.id]
                auth_user: AuthUser = db_user.get_auth()
            except ConfigurationError:
                raise AuthException(AuthFailReason.username, f"Not inicialized user model: {User})", 500)
            except Exception:
                raise AuthException(AuthFailReason.username, f"No user#{auth_user.id}({auth_user.username})", 404)
            return self._user2tok(auth_user)

        self.routes = {
            "refresh": (refresh, "GET"),
            "tg-token": (self.tgd2tok, "POST"),
            "tga-token": (self.tid2tok, "POST"),
        }

    # API ENDOINTS
    async def _twa2tok(self, twa_user: WebAppUser, bot_token: str, expire: timedelta) -> Token:  # _common
        db_user: User = await user_upsert(twa_user, user_model=self.db_user_model)
        auth_user: AuthUser = db_user.get_auth()
        access_token = jwt_encode(auth_user, bot_token, expire)
        token = Token(access_token=access_token, user=auth_user)
        resp = JSONResponse(token.model_dump())
        resp.set_cookie("access_token", token.access_token)
        return resp

    # login for api endpoint
    async def tgd2tok(self, data: TgData) -> Token:  # widget
        dct = {k: v for k, v in data.model_dump().items() if v is not None}
        if not check_signature(self.secret, dct.pop("hash"), **dct):
            raise AuthException(AuthFailReason.signature, "Tg initData invalid")
        return await self._twa2tok(WebAppUser(**dct), self.secret, expire=self.expires)

    async def tid2tok(self, tid: str) -> Token:  # twa
        try:
            twaid: WebAppInitData = safe_parse_webapp_init_data(token=self.secret, init_data=tid)
        except ValueError:
            raise AuthException(AuthFailReason.signature, "Tg Initdata invalid")
        return await self._twa2tok(twaid.user, self.secret, expire=self.expires)
