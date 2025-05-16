from django.urls import path
from diary.views import DiaryEntriesView, DiaryEntryCreateView

urlpatterns = [
    path('', DiaryEntriesView.as_view(), name='entries-list'),
    path('create/', DiaryEntryCreateView.as_view(), name='entries-create'),
]