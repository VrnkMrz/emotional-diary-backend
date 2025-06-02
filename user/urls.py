from django.urls import path
from .views      import ProfileView, CommanderCheckView

urlpatterns = [
    path('profile/',       ProfileView.as_view(),        name='profile'),
    path('is_commander/',  CommanderCheckView.as_view(), name='is_commander'),
]
