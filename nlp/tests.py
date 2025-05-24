from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import jwt
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Users, Emotions
import nlp.views as views


class NLPClassificationFormatTest(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.user = Users.objects.create(
            name='Tester',
            surname='One',
            birthday_year=1990,
            birthday_month=1,
            birthday_day=1,
            email='tester@example.com',
            gender='other',
            password_hash='',
            created_at=now,
            updated_at=now,
            nickname='tester'
        )
        payload = {
            'user_id': self.user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        Emotions.objects.create(emotion_name='Щастя')

        self.url = reverse('analyze_emotion')

    def test_classification_returns_valid_format(self):
        dummy = SimpleNamespace(output_parsed=views.EmotionResponse(emotion='Щастя'))
        with patch.object(views.openai.responses, 'parse', return_value=dummy) as mock_parse:
            resp = self.client.post(self.url, {'text': 'Будь який текст'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('emotion', resp.data)
        self.assertIsInstance(resp.data['emotion'], str)

        mock_parse.assert_called_once()

    def test_classification_missing_text_field(self):
        resp = self.client.post(self.url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {"error": "Поле 'text' є обов'язковим."})
