from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


class CustomTokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth_header) == 1:
            msg = 'Неверный заголовок токена. Учётные данные не предоставлены.'
            raise AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = 'Неверный заголовок токена. Строка токена не должна содержать пробелов.'
            raise AuthenticationFailed(msg)

        try:
            token = auth_header[1].decode()
        except UnicodeError:
            msg = 'Неверный заголовок токена. Строка токена не должна содеражть запрещённые символы.'
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Неправильный токен.')

        if not token.user.is_active:
            raise AuthenticationFailed('Юзер неактивен или удалён.')

        return (token.user, token)
