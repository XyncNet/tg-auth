from aiogram.utils.auth_widget import check_signature
from aiogram.utils.web_app import WebAppUser, WebAppInitData, safe_parse_webapp_init_data
from pydantic import BaseModel
from x_auth import AuthException, AuthFailReason
from x_auth.pydantic import Token
from x_auth.router import AuthRouter

from tg_auth import User, _twa2tok


class TgData(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class TgRouter(AuthRouter):
    def __init__(self, secret: str, db_user_model: type(User) = User):
        super().__init__(secret, db_user_model)
        self.routes["tg-token"] = self.tgd2tok, "POST"
        self.routes["tga-token"] = self.tid2tok, "POST"

    # API ENDOINTS
    # login for api endpoint
    async def tgd2tok(self, data: TgData) -> Token:  # widget
        dct = {k: v for k, v in data.model_dump().items() if v is not None}
        if not check_signature(self.secret, dct.pop("hash"), **dct):
            raise AuthException(AuthFailReason.signature, "Tg initData invalid")
        return await _twa2tok(WebAppUser(**dct), self.secret, expire=self.expires)

    async def tid2tok(self, tid: str) -> Token:  # twa
        try:
            twaid: WebAppInitData = safe_parse_webapp_init_data(token=self.secret, init_data=tid)
        except ValueError:
            raise AuthException(AuthFailReason.signature, "Tg Initdata invalid")
        return await _twa2tok(twaid.user, self.secret, expire=self.expires)
