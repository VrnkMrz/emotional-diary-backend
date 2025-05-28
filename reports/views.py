# reports/views.py

from django.utils import timezone
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Diaryentries
from core.models import Emotions
from .serializers import (
    SummarySerializer,
    FirstEmotionSerializer,
    FrequencySerializer,
)

class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ym = request.query_params.get("month")
        if not ym:
            now = timezone.localdate()
            ym = now.strftime("%Y-%m")
        year, month = map(int, ym.split("-"))
        qs = Diaryentries.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        )
        total = qs.count()
        matches = qs.filter(user_emotion=F("ai_emotion")).count()
        pct = (matches / total * 100) if total else 0
        data = {"totalEntries": total, "matchCount": matches, "matchPct": pct}
        return Response(SummarySerializer(data).data)

class FirstEmotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ym = request.query_params.get("month")
        if not ym:
            now = timezone.localdate()
            ym = now.strftime("%Y-%m")
        year, month = map(int, ym.split("-"))
        qs = Diaryentries.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        ).order_by("date", "id")
        firsts = {}
        for entry in qs:
            if entry.date not in firsts:
                firsts[entry.date] = entry.user_emotion or entry.ai_emotion
        payload = [
            {"date": d, "firstEmotion": emo.emotion_name}
            for d, emo in firsts.items()
        ]
        return Response(FirstEmotionSerializer(payload, many=True).data)

class FrequenciesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ym = request.query_params.get("month")
        if not ym:
            now = timezone.localdate()
            ym = now.strftime("%Y-%m")
        year, month = map(int, ym.split("-"))
        base_qs = Diaryentries.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        )
        freqs = []
        for emo in Emotions.objects.all():
            u = base_qs.filter(user_emotion=emo).count()
            a = base_qs.filter(ai_emotion=emo).count()
            freqs.append({
                "emotion": emo.emotion_name,
                "userCount": u,
                "aiCount": a
            })
        return Response(FrequencySerializer(freqs, many=True).data)
