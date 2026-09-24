from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer

from .serializers import RegisterSerializer, VerifyOTPSerializer

from rest_framework import serializers


from .utils import create_and_send_otp
from .models import OTP
from .serializers import RequestPasswordResetSerializer, ResetPasswordSerializer


from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from .serializers import GoogleAuthSerializer



from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from .permissions import IsJobSeeker
from .serializers import JobSeekerProfileSerializer
from .models import JobSeekerProfile


from .permissions import IsCompany
from .serializers import CompanyProfileSerializer
from .models import CompanyProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            raise serializers.ValidationError(
                "Please verify your email before logging in."
            )

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        access_token = data['access']
        refresh_token = data['refresh']

        response = Response({'access': access_token}, status=200)

        response.set_cookie(
            key='refresh_token',
            value=str(refresh_token),
            httponly=True,
            secure=False,       # set True in production (requires HTTPS)
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,  # 7 days, matches SIMPLE_JWT setting
        )

        return response


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token not found.'}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=401)

        new_access_token = str(refresh.access_token)

        response = Response({'access': new_access_token}, status=200)

        try:
            refresh.blacklist()
        except AttributeError:
            pass

        user_id = refresh['user_id']
        user = User.objects.get(id=user_id)
        new_refresh = CustomTokenObtainPairSerializer.get_token(user)

        response.set_cookie(
            key='refresh_token',
            value=str(new_refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
        )

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        response = Response({'detail': 'Logged out successfully.'}, status=200)
        response.delete_cookie('refresh_token')

        return response



class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']

        user.is_verified = True
        user.save()

        otp.is_used = True
        otp.save()

        return Response({'detail': 'Email verified successfully.'}, status=200)




class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        create_and_send_otp(user, OTP.Purpose.PASSWORD_RESET)

        return Response({'detail': 'Password reset OTP sent to your email.'}, status=200)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        otp.is_used = True
        otp.save()

        return Response({'detail': 'Password reset successfully.'}, status=200)




class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['id_token']
        role = serializer.validated_data.get('role')

        try:
            idinfo = google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({'detail': 'Invalid Google token.'}, status=401)

        email = idinfo.get('email')
        email_verified = idinfo.get('email_verified')

        if not email or not email_verified:
            return Response({'detail': 'Google account email not verified.'}, status=401)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'role': role or User.Role.JOB_SEEKER,
                'is_verified': True,
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        refresh = CustomTokenObtainPairSerializer.get_token(user)
        access_token = str(refresh.access_token)

        response = Response({'access': access_token}, status=200)

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
        )

        return response


from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from .permissions import IsJobSeeker
from .serializers import JobSeekerProfileSerializer
from .models import JobSeekerProfile


class JobSeekerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]
    parser_classes = [MultiPartParser, FormParser,JSONParser]

    def get_object(self):
        profile, created = JobSeekerProfile.objects.get_or_create(user=self.request.user)
        return profile

from .permissions import IsCompany
from .serializers import CompanyProfileSerializer
from .models import CompanyProfile


class CompanyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        profile, created = CompanyProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'company_name': self.request.user.email}
        )
        return profile