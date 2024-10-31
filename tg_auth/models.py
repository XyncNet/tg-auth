from enum import IntEnum
from tortoise import fields
from x_auth.models import User as BaseUser


class UserStatus(IntEnum):  # accords with: aiogram.enums.chat_member_status.ChatMemberStatus
    CREATOR = 5
    ADMINISTRATOR = 4
    MEMBER = 3
    RESTRICTED = 2
    LEFT = 1
    KICKED = 0


class Lang(IntEnum):
    ru = 1
    en = 2


class User(BaseUser):
    id: int = fields.BigIntField(True)
    status: UserStatus = fields.IntEnumField(UserStatus, default=UserStatus.RESTRICTED)


class UserRefTrait:
    ref: fields.ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="proteges", null=True
    )
    ref_id: int | None


class UserInfoTrait:
    first_name: str | None = fields.CharField(95, null=True)
    last_name: str | None = fields.CharField(95, null=True)
    pic: str | None = fields.CharField(95, null=True)
    lang: Lang | None = fields.IntEnumField(Lang, default=Lang.ru, null=True)
