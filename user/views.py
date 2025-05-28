from django.shortcuts        import get_object_or_404
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from core.models            import Users, Diaryentries
from .serializers           import UserProfileSerializer, DiaryEntrySerializer

class ProfileView(RetrieveAPIView):
    """
       GET  /profile/   — перегляд профілю
       PATCH /profile/   — часткове оновлення профілю (наприклад, nickname)
       PUT   /profile/   — повне оновлення профілю
       """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # повертаємо поточного користувача
        return get_object_or_404(Users, id=self.request.user.id)

