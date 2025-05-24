from django.urls import path
from .views import EmotionClassificationView
from .views import EmotionPredictionView

urlpatterns = [
    path("analyze_emotion/", EmotionClassificationView.as_view(), name="analyze_emotion"),
    path('predict_emotions/', EmotionPredictionView.as_view(), name='predict_emotions'),
]
