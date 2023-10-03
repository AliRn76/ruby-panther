from panther import status
from panther.exceptions import APIException


class UsernameAlreadyExistsException(APIException):
    detail = 'Username Already Exists'
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidUsernameOrPasswordException(APIException):
    detail = 'Invalid Username Or Password'
    status_code = status.HTTP_400_BAD_REQUEST


class PhoneNumberAlreadyExistsException(APIException):
    detail = 'User With This PhoneNumber Already Exists'
    status_code = status.HTTP_400_BAD_REQUEST


class OTPIsInvalidOrExpiredException(APIException):
    detail = 'OTP Is Invalid Or Expired'
    status_code = status.HTTP_400_BAD_REQUEST
