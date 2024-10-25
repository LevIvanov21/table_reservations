from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG") == "True"

# change when hosting!
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "phonenumber_field",
    "users",
    "restaurant",
    "django_celery_beat",

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# # Чтобы кешировать весь сайт (вот насколько редко такое нужно?)
# MIDDLEWARE = [
#     'django.middleware.cache.UpdateCacheMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.cache.FetchFromCacheMiddleware',
# ]
# не забыть в .env CACHE_ENABLED=False установить после этого

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),

    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = (BASE_DIR / "static",)

# ENV_TYPE = os.getenv("ENV_TYPE")
#
# if ENV_TYPE == "local":
#     STATICFILES_DIRS = (BASE_DIR / "static",)
# else:
#     STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# email settings
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL") == "True"
SERVER_EMAIL = os.getenv("SERVER_EMAIL")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

LOGIN_URL = "/users/"

REDIRECT_FIELD_NAME = "users/login.html"

CORS_ALLOWED_ORIGINS = [os.getenv("CORS_ALLOWED_ORIGINS"), ]

CSRF_TRUSTED_ORIGINS = [os.getenv("CSRF_TRUSTED_ORIGINS"), ]

CORS_ALLOW_ALL_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS") == "True"

# Celery Configuration Options

# Часовой пояс для работы Celery
CELERY_TIMEZONE = TIME_ZONE
# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True
# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ENABLE_UTC = False
# URL-адрес брокера сообщений
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

CELERY_BEAT_SCHEDULE = {
    "restaurant.tasks.find_active_bookings": {
        "task": "restaurant.tasks.find_active_bookings",
        "schedule": timedelta(minutes=1),  # Run every day at 00:00
    }
}
# CELERY_BEAT_SCHEDULE = "django_celery_beat.schedulers:DatabaseScheduler"

TELEGRAM_URL = os.getenv("TELEGRAM_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

CACHE_ENABLED = os.getenv("CACHE_ENABLED") == "True"

if CACHE_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("LOCATION"),
            "TIMEOUT": 300  # Ручная регулировка времени жизни кеша в секундах, по умолчанию 300
        }
    }
