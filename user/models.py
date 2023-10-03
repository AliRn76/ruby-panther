from datetime import datetime
from typing import ClassVar

from panther.db import Model
from panther.db.models import IDType
from panther.file_handler import File
from pydantic import Field


class User(Model):
    PHONE_NUMBER_PATTERN: ClassVar = r'^(\+98|98|0)?(9\d{9})$'

    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(..., min_length=4, max_length=64)
    first_name: str = Field('', max_length=15)
    last_name: str = Field('', max_length=15)
    profile_picture: File | None = None
    phone_number: str = Field(None, pattern=PHONE_NUMBER_PATTERN)
    bio: str = Field(None, max_length=127)
    is_banned: bool = False
    is_male: bool = Field(None)
    is_admin: bool = False
    date_joined: datetime = datetime.now()
    last_login: datetime = None

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def update_last_login(self):
        self.update(last_login=datetime.now())


class Room(Model):
    is_pv: bool
    last_message: str = None
    is_pinned: bool = False
    is_muted: bool = False
    is_male: bool = None  # Gender of contact, Required in 'room_id is pv_id'
    name: str
    avatar: str = None
    is_last_from_me: bool = None
    room_id: IDType  # Can be 'pv_id' or 'gp_id'
    user_id: IDType

