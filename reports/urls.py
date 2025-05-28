
from django.urls import path
from .views import SummaryView, FirstEmotionsView, FrequenciesView

urlpatterns = [
    path("summary/", SummaryView.as_view(), name="reports-summary"),
    path("first-emotions/", FirstEmotionsView.as_view(), name="first-emotions"),
    path("frequencies/", FrequenciesView.as_view(), name="reports-frequencies"),
]
