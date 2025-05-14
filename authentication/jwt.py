import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from core.models import Users

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].lower() != b'bearer':
            return None
        if len(header) != 2:
            raise exceptions.AuthenticationFailed('Невірний формат токена')
        token = header[1]
        try:
            payload = jwt.decode(token,
                                 settings.JWT_SECRET,
                                 algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Токен прострочено')
        except jwt.PyJWTError:
            raise exceptions.AuthenticationFailed('Невірний токен')

        try:
            user = Users.objects.get(id=payload['user_id'])
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed('Користувач не знайдений')

        return (user, None)
