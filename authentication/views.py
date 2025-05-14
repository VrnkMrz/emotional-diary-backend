import secrets
import jwt
from datetime import datetime
from django.conf import settings
import secrets
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import bcrypt
from core.models import Users
from authentication.models import OTPRequest
from authentication.services import MailerSendService
import logging

logger = logging.getLogger(__name__)

class OTPInitiateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            payload = {'error': 'email is required'}
            resp = Response(payload, status=status.HTTP_400_BAD_REQUEST)
            logger.info("OTPInitiateView response: %s", payload)
            return resp

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            payload = {'error': 'user not found'}
            resp = Response(payload, status=status.HTTP_404_NOT_FOUND)
            logger.info("OTPInitiateView response: %s", payload)
            return resp

        secret = secrets.token_hex(3)  
        expires = datetime.utcnow() + timedelta(minutes=5)

        OTPRequest.objects.create(
            user=user,
            secret=secret,
            expires_at=expires
        )

        try:
            MailerSendService().send_otp(email, secret)
        except Exception as e:
            print("MailerSend failed:", e)

        return Response({'success': True})

class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        if not email or not otp_code:
            return Response(
                {'error': 'email та otp обовʼязкові поля'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({'error': 'Користувача не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        otp_entry = (
            OTPRequest.objects
            .filter(
                user=user,
                secret=otp_code,
                used=False,
                expires_at__gte=timezone.now()
            )
            .order_by('-created_at')
            .first()
        )

        if not otp_entry:
            return Response(
                {'error': 'Невірний або протермінований код'},
                status=status.HTTP_400_BAD_REQUEST
            )
        otp_entry.used = True
        otp_entry.save(update_fields=['used'])
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXP_DELTA_HOURS),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        return Response({'token': token})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'email і password обовʼязкові поля'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response(
                {'error': 'Користувача не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )

        stored_hash = user.password_hash or ''
        if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return Response(
                {'error': 'Невірний пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        secret = f"{secrets.randbelow(10 ** 6):06d}"  
        expires = timezone.now() + timedelta(minutes=5)

        OTPRequest.objects.create(
            user=user,
            secret=secret,
            expires_at=expires,
            used=False
        )

        try:
            MailerSendService().send_otp(to_email=email, otp_code=secret)
        except Exception as e:
            print("MailerSendService failed:", e)

        return Response(
            {'success': True, 'detail': 'Пароль вірний, надіслано OTP'},
            status=status.HTTP_200_OK
        )