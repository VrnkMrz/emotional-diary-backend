from django.urls import path
from .views import EmotionClassificationView

urlpatterns = [
    path("analyze_emotion/", EmotionClassificationView.as_view(), name="analyze_emotion"),
]
