from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.models import Diaryentries
from diary.serializers import DiaryEntrySerializer

class MyDiaryEntriesView(ListAPIView):
    serializer_class = DiaryEntrySerializer
    permission_classes = [AllowAny]    # залишаємо, якщо потрібен AllowAny

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Diaryentries.objects.none()
        return (
            Diaryentries.objectsS
            .filter(user=user)
            .order_by('-date')
        )
