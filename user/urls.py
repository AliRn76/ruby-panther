from user.apis import RegisterAPI, LoginAPI, CheckUsernameAPI, RefreshTokenAPI, SubmitPhoneAPI, SubmitOTPAPI, \
    ForgetPasswordAPI, NewPasswordAPI, MyProfileAPI

urls = {
    'register/': RegisterAPI,
    'login/': LoginAPI,
    'check-username/': CheckUsernameAPI,
    'refresh/': RefreshTokenAPI,

    'submit-phone/': SubmitPhoneAPI,
    'submit-otp/': SubmitOTPAPI,

    'forget-password/': ForgetPasswordAPI,
    'new-password/': NewPasswordAPI,
    'profile/': MyProfileAPI,
    # 'profile/<user_id>/': ...,
    # 'profile/picture/': ...,
    # 'room/': ...,
    # 'room/<user_room_id>/': ...,
    # 'contact/': ...,
}
