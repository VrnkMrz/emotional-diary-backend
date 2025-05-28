from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('authentication.urls')),
    path('api/user/', include('user.urls')),

    path('api/entries/', include('diary.urls')),
    path('api/nlp/', include('nlp.urls')),
    path("api/reports/", include("reports.urls")),

]
