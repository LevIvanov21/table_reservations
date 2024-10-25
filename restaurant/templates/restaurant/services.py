from django.core.cache import cache

from restaurant.models import Booking, Questions
from config import settings


def get_cached_booking_list(recached: bool = False):
    if settings.CACHE_ENABLED:
        key = "booking_list"
        if recached:
            booking_list = Booking.objects.all()
            cache.set(key, booking_list)
        else:
            booking_list = cache.get(key)
            if booking_list is None:
                booking_list = Booking.objects.all()
                cache.set(key, booking_list)
    else:
        booking_list = Booking.objects.all()
    return booking_list


def get_cached_questions_list(recached: bool = False):
    if settings.CACHE_ENABLED:

        key = "questions_list"
        if recached:
            questions_list = Questions.objects.all()
            cache.set(key, questions_list)

        else:
            questions_list = cache.get(key)
            if questions_list is None:
                questions_list = Questions.objects.all()
                cache.set(key, questions_list)
    else:
        questions_list = Questions.objects.all()
    return questions_list


def cache_delete_booking_list():
    key = "booking_list"
    cache.delete(key)


def cache_delete_question_list():
    key = "questions_list"
    cache.delete(key)


def cache_clear():
    cache.clear()
