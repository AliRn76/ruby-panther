from datetime import datetime

from panther.file_handler import File
from panther.utils import encrypt_password
from pydantic import BaseModel, field_validator, Field, model_validator

from core import cache
from core.configs import OTP_LEN
from user.exceptions import UsernameAlreadyExistsException, InvalidUsernameOrPasswordException, \
    PhoneNumberAlreadyExistsException, OTPIsInvalidOrExpiredException
from user.models import User


class RegisterSerializer(BaseModel):
    username: str = User.model_fields['username']
    password: str = User.model_fields['password']

    @field_validator('username')
    def check_username(cls, username):
        if User.find_one(username=username):
            raise UsernameAlreadyExistsException
        return username

    @field_validator('password')
    def encrypt_password(cls, password):
        return encrypt_password(password=password)


class LoginSerializer(BaseModel):
    username: str = User.model_fields['username']
    password: str = User.model_fields['password']

    @field_validator('username')
    def validate_username(cls, username):
        cls.user = User.find_one_or_raise(username=username)
        return username

    @field_validator('password')
    def validate_password(cls, password):
        hashed_password = encrypt_password(password=password)
        if cls.user.password != hashed_password:
            raise InvalidUsernameOrPasswordException
        return password


class CheckUsernameSerializer(BaseModel):
    username: str = User.model_fields['username']

    @field_validator('username')
    def check_username(cls, username):
        if User.find_one(username=username):
            raise UsernameAlreadyExistsException
        return username


class PhoneNumberSerializer(BaseModel):
    phone_number: str = Field(pattern=User.PHONE_NUMBER_PATTERN)

    @field_validator('phone_number')
    def check_user(cls, phone_number):
        if User.find_one(phone_number=phone_number):
            raise PhoneNumberAlreadyExistsException
        return phone_number


class SubmitOTPSerializer(BaseModel):
    otp: str = Field(min_length=OTP_LEN, max_length=OTP_LEN)


class ForgetPasswordSerializer(PhoneNumberSerializer):
    phone_number: str = Field(pattern=User.PHONE_NUMBER_PATTERN)

    @field_validator('phone_number')
    def check_user(cls, phone_number):
        cls.user = User.find_one_or_raise(phone_number=phone_number)
        return phone_number


class NewPasswordSerializer(SubmitOTPSerializer):
    password: str = User.model_fields['password']

    @field_validator('otp')
    def check_otp(cls, otp):
        if user_id := cache.get_forget_password_otp(otp=otp):
            cls.user = User.find_one(id=user_id)
        else:
            raise OTPIsInvalidOrExpiredException

    @field_validator('password')
    def encrypt_password(cls, password):
        return encrypt_password(password=password)


class ProfileSerializer(BaseModel):
    username: str = Field('', min_length=3, max_length=15)
    first_name: str = User.model_fields['first_name']
    last_name: str = User.model_fields['last_name']
    profile_picture: File | None = None
    bio: str = User.model_fields['bio']
    is_male: bool | None = None


class RetrieveProfileSerializer(ProfileSerializer):
    phone_number: str
    date_joined: datetime
    last_login: datetime
