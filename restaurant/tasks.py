from datetime import datetime, timedelta
from celery import shared_task

from restaurant.services import send_telegram_message, send_email_message
from restaurant.utils.utils import get_actual_bookings, time_segment


@shared_task
def send_information_about_bookings(message, tg_chat_id):
    """Отправляет сообщение пользователю о поставленном лайке"""
    send_telegram_message(message, tg_chat_id)


@shared_task
def celery_send_mail(subject, message, recipient_list):
    send_email_message(subject, message, recipient_list)
    #
    # send_mail(
    #     subject=subject,
    #     message=message,
    #     from_email=from_email,
    #     recipient_list=recipient_list
    # )


@shared_task
def find_active_bookings():
    utc_time = datetime.now().replace(second=0, microsecond=0)

    # там уже есть актуальное время
    bookings = get_actual_bookings(active=True, time_start=True).filter(notification__in=[1, 2, 3])

    # получим местное время через user
    for b in bookings:
        start = (time_segment(b.date_field, b.time_start, b.time_end)[0] - timedelta(hours=b.notification))
        notification = (start - timedelta(hours=b.notification)).replace(second=0, microsecond=0)
        time = (utc_time + timedelta(hours=b.user.time_offset)).replace(second=0, microsecond=0)

        print(f"start {start}, time{time}, notification {notification}")

        tg_chat_id = b.user.tg_chat_id

        if tg_chat_id is not None:
            if notification == time:
                message = (f"Вы забронировали столик [{b.table}]: Время: [{b.time_start} - {b.time_end}], "
                           f"дата: [{b.date_field}]")
                send_information_about_bookings.delay(message, tg_chat_id)
            # # использовал для проверки работы программы
            # else:
            #     message = f"start {start}, time{time}, notification {notification}"

            send_information_about_bookings.delay(tg_chat_id, message)
        # # использовал для проверки работы программы
        # else:
        # send_information_about_bookings.delay("1567728836",f"No telegram for User {b.user}")
