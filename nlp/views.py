import os
import json
import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pydantic import BaseModel

from core.models import Emotions

openai.api_key = os.getenv("OPENAI_API_KEY")
#openai.api_key = "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"

class EmotionResponse(BaseModel):
    emotion: str

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
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": "Класифікуй текст в одну з емоцій: "
                            "Гнів, Відраза, Страх, Тривога, Сум, Щастя, Розслаблення, Бажання. ",
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
