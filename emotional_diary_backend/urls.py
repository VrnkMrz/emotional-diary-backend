# emotional_diary_backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('authentication.urls')),
    path('api/user/', include('user.urls')),

    # замість окремих ендпоінтів тут
    path('api/entries/', include('diary.urls')),
]
