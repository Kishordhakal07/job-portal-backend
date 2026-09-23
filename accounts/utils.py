from django.core.mail import send_mail
from django.conf import settings
from .models import OTP


def create_and_send_otp(user, purpose):
    code = OTP.generate_code()

    OTP.objects.create(
        user=user,
        code=code,
        purpose=purpose,
    )

    subject = 'Your Job Portal Verification Code'
    message = f'Your OTP code is: {code}\n\nThis code expires in 10 minutes.'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )