import datetime
from bleach import clean
import markdown
from django import template
import random
import string


from django.utils.safestring import mark_safe

register = template.Library()


# Создание тега
@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)


@register.filter
def time_to_local(value, arg):
    # меняет время на локальное получив разницу часовых поясов в часах
    created_at_local = value + datetime.timedelta(hours=arg)
    return created_at_local


@register.filter
def has_been(value, arg):
    now = datetime.datetime.now()
    booking_datetime = datetime.datetime(year=value.year, month=value.month,
                                         day=value.day, hour=arg.hour,
                                         minute=arg.minute)
    if booking_datetime > now:
        return False
    return True


@register.filter
def time_offset(value, arg):
    time = value + datetime.timedelta(hours=arg)

    return time


# Создание тега
@register.simple_tag
def generate_fake_mail(length: int = 10) -> object:
    # length = int(s_length)
    letters = string.ascii_letters + string.digits  # + string.punctuation
    mail = "".join(random.choice(letters) for _ in range(length))

    letters2 = string.ascii_lowercase
    mail2 = "".join(random.choice(letters2) for _ in range(length // 2))
    return f"{mail}@{mail2}.com"


# Создание фильтра
@register.filter
def last_five_contacts(query_set):
    number = len(query_set)
    if number <= 5:
        return query_set
    else:
        return query_set[number - 5: number + 1]


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"

    return "/static/image/no_image.png"


@register.filter()
def user_media_filter(path):
    if path:
        return f"/media/{path}"

    return "/static/image/no_avatar.png"


def markdown_comment(value):
    return clean(
        markdown.markdown(value, extensions=["nl2br"]),
        strip=True,
        tags=["strong", "b", "li", "u", "blockquote", "br"])


@register.filter
def comment_markdown(value):
    return mark_safe(markdown_comment(value))
