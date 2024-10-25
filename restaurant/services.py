# from django.contrib.sites import requests
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
from config import settings
import requests


def send_telegram_message(chat_id, message):
    """Функция отправки сообщения в телеграм"""

    params = {
        "text": message,
        "chat_id": chat_id,
    }
    requests.get(f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage", params=params)


def send_email_message(subject, message, recipient_list):
    print(f"subject = {subject}, message = {message}, from_email (EMAIL_HOST_USER) = {EMAIL_HOST_USER}, "
          f"recipient_list = {recipient_list}")

    send_mail(
        subject=subject,
        message=str(message),
        from_email=EMAIL_HOST_USER,
        recipient_list=recipient_list
    )
