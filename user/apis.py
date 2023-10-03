from datetime import timedelta

from panther import status
from panther.app import GenericAPI
from panther.authentications import JWTAuthentication
from panther.request import Request
from panther.response import Response
from panther.throttling import Throttling

from core import cache
from core.configs import OTP_EXP_SECOND
from user.exceptions import UsernameAlreadyExistsException
from user.models import User
from user.serializers import RegisterSerializer, LoginSerializer, CheckUsernameSerializer, PhoneNumberSerializer, \
    SubmitOTPSerializer, ForgetPasswordSerializer, NewPasswordSerializer, ProfileSerializer, RetrieveProfileSerializer
from user.utils import send_otp, generate_otp


class RegisterAPI(GenericAPI):
    input_model = RegisterSerializer

    def post(self, request: Request):
        payload: RegisterSerializer = request.validated_data
        user = User.insert_one(username=payload.username, password=payload.password)
        user.update_last_login()
        data = {
            'access_token': JWTAuthentication.encode_jwt(user_id=user.id),
            'refresh_token': JWTAuthentication.encode_refresh_token(user_id=user.id)
        }
        return Response(data=data, status_code=status.HTTP_201_CREATED)


class LoginAPI(GenericAPI):
    input_model = LoginSerializer

    def post(self, request: Request):
        user = request.validated_data.user
        user.update_last_login()
        data = {
            'access_token': JWTAuthentication.encode_jwt(user_id=user.id),
            'refresh_token': JWTAuthentication.encode_refresh_token(user_id=user.id)
        }
        return Response(data=data, status_code=status.HTTP_200_OK)


class CheckUsernameAPI(GenericAPI):
    input_model = CheckUsernameSerializer

    def post(self, request: Request):
        return Response(status_code=status.HTTP_200_OK)


class RefreshTokenAPI(GenericAPI):
    auth = True

    def post(self, request: Request):
        data = {
            'access_token': JWTAuthentication.encode_jwt(user_id=request.user.id),
            'refresh_token': JWTAuthentication.encode_refresh_token(user_id=request.user.id)
        }
        return Response(data=data, status_code=status.HTTP_200_OK)


class SubmitPhoneAPI(GenericAPI):
    auth = True
    input_model = PhoneNumberSerializer
    throttling = Throttling(rate=2, duration=timedelta(minutes=1))

    def post(self, request: Request):
        phone_number = request.validated_data.phone_number
        otp = generate_otp()
        cache.set_otp_data(user_id=request.user.id, phone_number=phone_number, otp=otp)
        send_otp(phone_number=phone_number, otp=otp)
        data = {'detail': 'OTP Sent Successfully.', 'timer': OTP_EXP_SECOND}
        return Response(data=data, status_code=status.HTTP_202_ACCEPTED)


class SubmitOTPAPI(GenericAPI):
    auth = True
    input_model = SubmitOTPSerializer
    throttling = Throttling(rate=10, duration=timedelta(minutes=2))

    def post(self, request: Request):
        if otp_data := cache.get_otp(request.user.id):
            if request.validated_data.otp == str(otp_data['otp']):
                request.user.update(phone_number=otp_data['phone_number'])
                return Response(status_code=status.HTTP_200_OK)
            else:
                data = {'detail': 'OTP is invalid'}
        else:
            data = {'detail': 'OTP is expired'}

        return Response(data=data, status_code=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordAPI(GenericAPI):
    input_model = ForgetPasswordSerializer

    def post(self, request: Request):
        cache.set_forget_password_otp(user_id=request.validated_data.user.id, otp=generate_otp())
        data = {'detail': 'OTP Sent Successfully.', 'timer': OTP_EXP_SECOND}
        return Response(data=data, status_code=status.HTTP_200_OK)


class NewPasswordAPI(GenericAPI):
    input_model = NewPasswordSerializer

    def post(self, request: Request):
        validated_data = request.validated_data
        validated_data.user.update(password=validated_data.password)
        data = {'detail': 'Password Changed Successfully.'}
        return Response(data=data, status_code=status.HTTP_200_OK)


class MyProfileAPI(GenericAPI):
    auth = True
    input_model = ProfileSerializer
    output_model = RetrieveProfileSerializer
    cache = True
    cache_exp_time = timedelta(minutes=1)

    def put(self, request: Request):
        data: ProfileSerializer = request.validated_data
        if request.user.username != data.username and User.find_one(username=data.username):
            raise UsernameAlreadyExistsException

        request.user.update(
            username=data.username or request.user.username,
            first_name=data.first_name or request.user.first_name,
            last_name=data.last_name or request.user.last_name,
            profile_picture=data.profile_picture or request.user.profile_picture,
            bio=data.bio or request.user.bio,
            is_male=data.is_male or request.user.is_male,
        )
        return Response(status_code=status.HTTP_202_ACCEPTED)

    def get(self, request: Request):
        return request.user
