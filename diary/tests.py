# diary/tests.py

import os
import binascii
from datetime import datetime, timedelta

import jwt
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APITestCase
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.models import Users, Emotions


class DiaryEntryAPITest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create(
            name='Tester',
            surname='One',
            birthday_year=1990,
            birthday_month=1,
            birthday_day=1,
            email='tester@example.com',
            gender='other',
            password_hash='',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            nickname='tester'
        )

        payload = {
            'user_id': self.user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.emotion = Emotions.objects.create(emotion_name='happy')

        key = binascii.unhexlify(settings.AES_ENCRYPTION_KEY_HEX)
        aesgcm = AESGCM(key)
        self.plaintext = "Це тестовий запис для перевірки шифрування".encode("utf-8")
        self.iv = os.urandom(12)
        ct_and_tag = aesgcm.encrypt(self.iv, self.plaintext, None)
        self.ciphertext = ct_and_tag[:-16]
        self.auth_tag   = ct_and_tag[-16:]
        self.encrypted_text_hex = binascii.hexlify(self.ciphertext).decode()
        self.iv_hex             = binascii.hexlify(self.iv).decode()
        self.tag_hex            = binascii.hexlify(self.auth_tag).decode()

        self.url = reverse('entries-list')

    def test_create_entry_success_and_get(self):
        data = {
            'encrypted_text': self.encrypted_text_hex,
            'iv':             self.iv_hex,
            'auth_tag':       self.tag_hex,
            'user_emotion':   self.emotion.id,
            'ai_emotion':     self.emotion.id,
            'date':           '2025-05-23'
        }
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp2 = self.client.get(self.url)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(
            resp2.data[0]['decrypted_text'],
            self.plaintext.decode('utf-8')
        )

    def test_create_entry_missing_encrypted_text(self):
        data = {
            'iv':           self.iv_hex,
            'auth_tag':     self.tag_hex,
            'user_emotion': self.emotion.id,
            'ai_emotion':   self.emotion.id,
        }
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_create_entry_missing_user_emotion(self):
        data = {
            'encrypted_text': self.encrypted_text_hex,
            'iv':             self.iv_hex,
            'auth_tag':       self.tag_hex,
            'ai_emotion':     self.emotion.id,
        }
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, 400)