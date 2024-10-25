from datetime import datetime, timedelta, time
from restaurant.models import ContentText, ContentImage, Contentlink, ContentParameters, Booking


def get_content_text_from_postgres(title):
    try:
        return ContentText.objects.get(title=title).body
    except Exception:
        return f"Для изменения текста создайте запись '{title}' в таблице ContentText (необходимы полномочия администратора)"


def get_content_image_from_postgres(title):
    try:
        return ContentImage.objects.get(title=title)
    except Exception:
        str_part_1 = "Для изменения изображения создайте запись '"
        str_part_2 = "' в таблице ContentImage и загрузите изображение (необходимы полномочия администратора)"
        description = f"{str_part_1}{title}{str_part_2}"

        try:
            not_found = ContentImage.objects.create(title="not_found", description=description, image=None)
        except Exception:
            not_found = ContentImage.objects.filter(title="not_found")
        return not_found


def get_content_link_from_postgres(title):
    try:
        return Contentlink.objects.get(title=title)
    except Exception:
        text = f"Для создания ссылки создайте запись '{title}' в таблице ContentLink (необходимы полномочия администратора)"
        try:
            not_found = Contentlink.objects.create(title="not_found", text="ссылка не найдена", link="#", description=text)
        except Exception:
            not_found = Contentlink.objects.filter(title="not_found")
        return not_found


def time_segment(date: datetime.date, start: datetime.time, end: datetime.time) -> tuple[datetime, datetime]:
    # делает из даты, начального и конечного времени 2 значения datetime

    t_start = datetime(year=date.year, month=date.month, day=date.day, hour=start.hour, minute=start.minute)
    t_end = datetime(year=date.year, month=date.month, day=date.day, hour=end.hour, minute=end.minute)
    if end < start:
        t_end += timedelta(days=1)

    return t_start, t_end


def get_content_parameters(ignored_error):
    # выдернуть из базы данных параметры работы, бронирования и т.д.

    # period_of = ContentParameters.objects.filter(title="period_of_booking").exists()
    # work_start = ContentParameters.objects.filter(title="work_start").exists()
    # work_end = ContentParameters.objects.filter(title="work_end").exists()
    # confirm_t = ContentParameters.objects.filter(title="confirm_timedelta").exists()
    #
    # if not (period_of and work_start and work_end and confirm_t):
    #     if ignored_error:
    #         work_start = time(8, 0, 0)
    #         work_end = time(23, 0, 0)
    #         period_of_booking = 14
    #         return {"period_of_booking": period_of_booking, "work_start": work_start, "work_end": work_end,
    #                 "confirm_timedelta": 45}
    #     else:
    #         return False
    try:
        period_of_booking = int(ContentParameters.objects.get(title="period_of_booking").body)
        work_start = time.fromisoformat(ContentParameters.objects.get(title="work_start").body)
        work_end = time.fromisoformat(ContentParameters.objects.get(title="work_end").body)
        confirm_timedelta = int(str(ContentParameters.objects.get(title="confirm_timedelta").body))

        return {"period_of_booking": period_of_booking, "work_start": work_start, "work_end": work_end,
                "confirm_timedelta": confirm_timedelta}
    except Exception:
        if ignored_error:
            work_start = time(8, 0, 0)
            work_end = time(23, 0, 0)
            period_of_booking = 14
            return {"period_of_booking": period_of_booking, "work_start": work_start, "work_end": work_end,
                    "confirm_timedelta": 45}
        else:
            return False


def get_actual_bookings(active=True, time_start=True):

    # 1) все неактивные бронирования проигнорим

    # booking_tokens = [token.booking.pk for token in BookingToken.objects.filter(created_at__gt=time_border)]

    now = datetime.now()

    if active:
        first_filter = Booking.objects.filter(active=True)
    else:
        first_filter = Booking.objects.all()

    second_filter = first_filter.filter(date_field__year__gte=now.year, date_field__month__gte=now.month,
                                        date_field__day__gte=(now - timedelta(days=1)).day)

    if (time_start):
        still_is = [b.pk for b in second_filter if
                    (time_segment(b.date_field, b.time_start, b.time_end)[0] > (now + timedelta(hours=b.user.time_offset)))]

        third_filter = second_filter.filter(pk__in=still_is)
    else:
        still_is = [b.pk for b in second_filter if
                    (time_segment(b.date_field, b.time_start, b.time_end)[1] > (now + timedelta(hours=b.user.time_offset)))]

        third_filter = second_filter.filter(pk__in=still_is)

    return third_filter
