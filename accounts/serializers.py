from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import create_and_send_otp
from .models import OTP

from .models import Skill, JobSeekerProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
        )
        create_and_send_otp(user, OTP.Purpose.REGISTRATION)
        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        try:
            otp = OTP.objects.filter(
                user=user,
                code=code,
                purpose=OTP.Purpose.REGISTRATION,
                is_used=False,
            ).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used OTP.")

        if otp.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs



class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        try:
            otp = OTP.objects.filter(
                user=user,
                code=code,
                purpose=OTP.Purpose.PASSWORD_RESET,
                is_used=False,
            ).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used OTP.")

        if otp.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)





class JobSeekerProfileSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True
    )
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = JobSeekerProfile
        fields = ['id', 'email', 'bio', 'skills', 'cv', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = [skill.name for skill in instance.skills.all()]
        return representation

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)

        instance.bio = validated_data.get('bio', instance.bio)

        if 'cv' in validated_data:
            instance.cv = validated_data['cv']

        instance.save()

        if skills_data is not None:
            skill_objects = []
            for skill_name in skills_data:
                skill, created = Skill.objects.get_or_create(name=skill_name.strip())
                skill_objects.append(skill)
            instance.skills.set(skill_objects)

        return instance