import os
import json
import openai
import logging
from typing import List
from django.conf import settings
import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pydantic import BaseModel, RootModel

from core.models import Emotions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# api_key = MAILERSEND_API_TOKEN
openai.api_key = settings.OPENAI_API_KEY
#openai.api_key =

class EmotionResponse(BaseModel):
    emotion: str

class TwoEmotions(BaseModel):
    emotions: List[str]

class EmotionClassificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response(
                {"error": "Поле 'text' є обов'язковим."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = openai.responses.parse(
                model="gpt-o4-mini",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Ти — мовна модель, яка класифікує емоційний стан тексту для щоденника військовослужбовця. "
                            "Не класифікуй емоцію лише за словами. "
                            "Визнач емоцію, яка найбільш передає стан автора тексту, "
                            "враховуючи контекст, навіть якщо присутні слова, які зазвичай мають інший емоційний відтінок."
                            "Обирай **тільки одну** з наступного списку, "
                            "яка найкраще передає основний емоційний настрій:\n\n"
                            "- **Гнів** — лють, роздратування, злість.\n"
                            "- **Огида** — відраза, презирство.\n"
                            "- **Страх** — жах, тривога, переляк.\n"
                            "- **Занепокоєння** — нервозність, напруженість, скутість, неспокій.\n"
                            "- **Смуток** — горе, страждання, депресія, розчарування.\n"
                            "- **Щастя** — бадьорість, радість, ентузіазм, задоволення.\n"
                            "- **Прагнення** — потяг, бажання, жага.\n"
                            "- **Розслаблення** — спокій, безтурботність, відпочинок, насолода, заспокоєння.\n\n"
                            "Відповідь має містити тільки назву обраної емоції, без пояснень і додаткових символів."
                        )
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0,
                text_format=EmotionResponse,
            )
            emotion_name = response.output_parsed.emotion
        except Exception as e:
            print(f"Exception: {e}")
            return Response(
                {"error": "Не вдалося визначити емоцію через OpenAI."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            emotion_obj = Emotions.objects.get(emotion_name__iexact=emotion_name)
        except Emotions.DoesNotExist:
            return Response(
                {"error": f"Невідома емоція: {emotion_name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"emotion": emotion_obj.emotion_name},
            status=status.HTTP_200_OK,
        )

class EmotionPredictionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")

        if not text:
            logging.warning("Missing 'text' in request")
            return Response(
                {"error": "Поле 'text' є обов'язковим."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            print("api key:", openai.api_key)
            parsed = openai.responses.parse(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Ти — модель, яка аналізує текст і вибирає два найімовірніші "
                            "емоційні стани з переліку: Гнів, Відраза, Страх, Тривога, Сум, "
                            "Щастя, Розслаблення, Прагнення. "
                            "Поверни строго JSON-об’єкт виду "
                            "{\"emotions\":[\"Щастя\",\"Тривога\"]}"
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                text_format=TwoEmotions,
            )
            emotions = parsed.output_parsed.emotions

            if len(emotions) != 2:
                raise ValueError(f"Очікував 2 емоції, отримав {len(emotions)}: {emotions}")

        except Exception  as e:
            return Response(
                {"error": "Не вдалося визначити дві емоції через OpenAI. {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Шукаємо кожну емоцію в БД і формуємо відповідь
        result = []
        for name in emotions:
            try:
                emo = Emotions.objects.get(emotion_name__iexact=name)
            except Emotions.DoesNotExist:
                return Response(
                    {"error": f"Невідома емоція: {name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            result.append({"emotion": emo.emotion_name})

        return Response(result, status=status.HTTP_200_OK)