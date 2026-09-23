from django.urls import path
from .views import (
    RegisterView, LoginView, RefreshView, LogoutView,
    VerifyOTPView, RequestPasswordResetView, ResetPasswordView,GoogleAuthView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
     path('google/', GoogleAuthView.as_view(), name='google-auth'),
]