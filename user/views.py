from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from core.models import Users
from .serializers import UserProfileSerializer

class ProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # self.request.user.id – це id із таблиці auth_user,
        # якщо воно співпадає з id у users – ок, якщо ні, можна взяти
        return Users.objects.get(id=self.request.user.id)
