import json
from panther.db.models import IDType

from panther.db.connection import redis

from core.configs import OTP_EXP_SECOND


# # # OTP
OTP_CACHE_KEY = 'otp_{user_id}'
FORGET_PASSWORD_CACHE_KEY = 'forget_password_otp_{otp}'


def set_otp_data(user_id: IDType, otp: int, phone_number: str):
    data = {'otp': otp, 'phone_number': phone_number}
    redis.set(name=OTP_CACHE_KEY.format(user_id=user_id), value=json.dumps(data), ex=OTP_EXP_SECOND)


def get_otp(user_id: IDType) -> dict:
    otp = redis.get(OTP_CACHE_KEY.format(user_id=user_id)) or b'{}'
    return json.loads(otp.decode())


# # # Forget Password
def set_forget_password_otp(user_id: IDType, otp: int):
    redis.set(FORGET_PASSWORD_CACHE_KEY.format(otp=otp), user_id, ex=OTP_EXP_SECOND)


def get_forget_password_otp(otp: int) -> str:
    user_id = redis.get(FORGET_PASSWORD_CACHE_KEY.format(otp=otp)) or b''
    return user_id.decode()
