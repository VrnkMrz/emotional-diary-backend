from django.contrib import admin
from django.urls import path, include
from diary.views     import MyDiaryEntriesView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('authentication.urls')),
    path('api/diary/entries/', MyDiaryEntriesView.as_view(), name='my_diary_entries'),
    path('api/user/', include('user.urls')),
]
