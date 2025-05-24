# diary/views.py
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from diary.serializers import DiaryEntrySerializer, DiaryEntryCreateSerializer
from core.models import Diaryentries
from rest_framework.generics import ListCreateAPIView

class DiaryEntriesView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Diaryentries.objects.filter(user=self.request.user).order_by('-date')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DiaryEntrySerializer
        return DiaryEntryCreateSerializer


class DiaryEntryCreateView(CreateAPIView):
    queryset           = Diaryentries.objects.all()
    serializer_class   = DiaryEntryCreateSerializer
    permission_classes = [IsAuthenticated]
