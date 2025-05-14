from django.urls import path
from .views import LoginView, OTPInitiateView, OTPVerifyView

urlpatterns = [
    path('login/',        LoginView.as_view(),       name='login'),
    path('otp/initiate/', OTPInitiateView.as_view(), name='otp_initiate'),
    path('otp/verify/',   OTPVerifyView.as_view(),   name='otp_verify'),
]
