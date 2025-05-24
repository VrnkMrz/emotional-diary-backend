import jwt
import bcrypt
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from rest_framework.test import APITestCase
from core.models import Users
from authentication.models import OTPRequest
from unittest.mock import patch

class AuthorizationBackendTests(APITestCase):
    def setUp(self):
        self.email = 'flow@example.com'
        self.password = 'FlowPass1'
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(self.password.encode(), salt).decode()

        now = timezone.now()

        self.user = Users.objects.create(
            name='Test',
            surname='User',
            birthday_year=1990,
            birthday_month=1,
            birthday_day=1,
            gender='unspecified',
            email=self.email,
            password_hash=hashed,
            created_at=now,
            updated_at=now,

        )

    def test_login_missing_fields(self):
        url = reverse('login')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'email і password обовʼязкові поля')

    def test_login_unknown_user(self):
        url = reverse('login')
        data = {'email': 'unknown@example.com', 'password': 'AnyPass1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Користувача не знайдено')

    def test_login_wrong_password(self):
        url = reverse('login')
        data = {'email': self.email, 'password': 'WrongPass1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Невірний пароль')

    @patch('authentication.services.MailerSendService.send_otp')
    def test_login_success_sends_otp(self, mock_send_otp):
        url = reverse('login')
        data = {'email': self.email, 'password': self.password}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIn('Пароль вірний', response.data['detail'])
        otp_qs = OTPRequest.objects.filter(user=self.user)
        self.assertTrue(otp_qs.exists())
        otp = otp_qs.latest('created_at')
        self.assertFalse(otp.used)
        self.assertGreater(otp.expires_at, timezone.now())
        mock_send_otp.assert_called_once_with(to_email=self.email, otp_code=otp.secret)

class OTPFlowTests(APITestCase):
    def setUp(self):
        self.email = 'flow@example.com'
        self.password = 'FlowPass1'
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(self.password.encode(), salt).decode()

        now = timezone.now()

        self.user = Users.objects.create(
            name='Test',
            surname='User',
            birthday_year=1990,
            birthday_month=1,
            birthday_day=1,
            gender='unspecified',
            email=self.email,
            password_hash=hashed,
            created_at=now,
            updated_at=now,
        )

    def test_otp_initiate_missing_email(self):
        url = reverse('otp_initiate')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'email is required')

    def test_otp_initiate_unknown_email(self):
        url = reverse('otp_initiate')
        response = self.client.post(url, {'email': 'noone@example.com'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'user not found')

    @patch('authentication.services.MailerSendService.send_otp')
    def test_otp_initiate_success(self, mock_send_otp):
        url = reverse('otp_initiate')
        response = self.client.post(url, {'email': self.email})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        otp = OTPRequest.objects.filter(user=self.user).latest('created_at')
        self.assertFalse(otp.used)
        self.assertGreater(otp.expires_at, timezone.now())
        mock_send_otp.assert_called_once_with(self.email, otp.secret)

    def test_otp_verify_missing_fields(self):
        url = reverse('otp_verify')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'email та otp обовʼязкові поля')

    def test_otp_verify_unknown_user(self):
        url = reverse('otp_verify')
        response = self.client.post(url, {'email': 'bad@example.com', 'otp': '123456'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Користувача не знайдено')

    def test_otp_verify_invalid_code(self):
        url = reverse('otp_verify')
        response = self.client.post(url, {'email': self.email, 'otp': 'wrong'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Невірний або протермінований код')

    def test_otp_verify_expired_code(self):
        expired = timezone.now() - timedelta(minutes=1)
        otp_obj = OTPRequest.objects.create(user=self.user, secret='expire123', expires_at=expired)
        url = reverse('otp_verify')
        response = self.client.post(url, {'email': self.email, 'otp': otp_obj.secret})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Невірний або протермінований код')

    def test_otp_verify_success_returns_jwt(self):
        valid_until = timezone.now() + timedelta(minutes=5)
        otp_obj = OTPRequest.objects.create(user=self.user, secret='valid123', expires_at=valid_until)
        url = reverse('otp_verify')
        response = self.client.post(url, {'email': self.email, 'otp': otp_obj.secret})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        token = response.data['token']
        decoded = jwt.decode(token,
                             settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        self.assertEqual(decoded['user_id'], self.user.id)
        self.assertIn('exp', decoded)
        self.assertIn('iat', decoded)
