from django.shortcuts        import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views      import APIView
from rest_framework.response   import Response
from django.db.models        import Count
from django.utils import timezone

from core.models import Users, Diaryentries, Company, Emotions
from .serializers           import UserProfileSerializer, DiaryEntrySerializer

class ProfileView(RetrieveUpdateAPIView):
    """
       GET  /profile/   — перегляд профілю
       PATCH /profile/ — часткове оновлення
       PUT   /profile/ — повне оновлення
    """
    serializer_class   = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Users, id=self.request.user.id)

class CommanderCheckView(APIView):
    """
    GET /api/reports/commander/?month=YYYY-MM
    — якщо користувач є командиром, повертає словник
      {<emotion_name>: <count>, ...} за вказаний місяць,
      де всі емоції присутні з мінімальним значенням 0.
    — якщо не командир — повертає порожній словник.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ym = request.query_params.get("month")
        if not ym:
            now = timezone.localdate()
            ym = now.strftime("%Y-%m")
        year, month = map(int, ym.split("-"))

        # Перевіряємо роль
        try:
            company = Company.objects.get(commander=request.user)
        except Company.DoesNotExist:
            return Response({})

        # Ініціалізуємо всі емоції з нульовим лічильником
        all_emotions = Emotions.objects.values_list("emotion_name", flat=True)
        result = {name: 0 for name in all_emotions}

        # Підрахунок ручних оцінок за обраний місяць
        qs = Diaryentries.objects.filter(
            user__company=company,
            user_emotion__isnull=False,
            date__year=year,
            date__month=month
        )
        agg = (
            qs
            .values("user_emotion__emotion_name")
            .annotate(count=Count("user_emotion"))
        )

        for item in agg:
            result[item["user_emotion__emotion_name"]] = item["count"]

        return Response(result)

