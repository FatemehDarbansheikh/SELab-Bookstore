from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
import logging


logger = logging.getLogger(__name__)


def send_notification_email(subject, message, recipient):
    """
    ارسال ایمیل اطلاع‌رسانی به کاربر
    خروجی: True اگر موفق، False اگر ناموفق
    """

    if not recipient:
        logger.warning('ایمیل دریافت‌کننده مشخص نشده است')
        return False

    try:
        send_mail(
            subject=subject,
            message=strip_tags(message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        logger.info(f'ایمیل با موفقیت به {recipient} ارسال شد')
        return True

    except Exception as e:
        logger.error(f'خطا در ارسال ایمیل به {recipient}: {e}')
        return False





