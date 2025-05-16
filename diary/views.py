# diary/views.py
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from diary.serializers import DiaryEntrySerializer, DiaryEntryCreateSerializer
from core.models import Diaryentries
from rest_framework.generics import ListCreateAPIView

class DiaryEntriesView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Повертаємо тільки ті записи, де foreign key user == поточний user
        return Diaryentries.objects.filter(user=self.request.user).order_by('-date')

    def get_serializer_class(self):
        # Для GET — "read" серіалізатор, для POST — "write"
        if self.request.method == 'GET':
            return DiaryEntrySerializer
        return DiaryEntryCreateSerializer


class DiaryEntryCreateView(CreateAPIView):
    queryset           = Diaryentries.objects.all()
    serializer_class   = DiaryEntryCreateSerializer
    permission_classes = [IsAuthenticated]
