from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

NULLABLE = {"blank": True, "null": True}


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        # email = self.normalize_email(email)
        # GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        # email = GlobalUserModel.normalize_username(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()
    username = None

    email = models.EmailField(max_length=150, verbose_name="почта", unique=True, help_text="Введите вашу почту")
    name = models.CharField(max_length=150, verbose_name="имя пользователя", help_text="Введите ваше имя", **NULLABLE)
    description = models.TextField(verbose_name="описание", help_text="Введите дополнительную информацию", **NULLABLE)
    phone_number = PhoneNumberField(**NULLABLE, verbose_name="телефон", help_text="Введите ваш номер телефона")
    avatar = models.ImageField(upload_to="users/avatars", verbose_name="аватар",
                               help_text="Выберите аватар", **NULLABLE)
    tg_nick = models.CharField(max_length=50, **NULLABLE, verbose_name="Tg name", help_text="Укажите telegram-ник",)
    tg_chat_id = models.CharField(max_length=50, verbose_name="Телеграм chat-id",
                                  help_text="Укажите телеграм chat-id", **NULLABLE,)
    time_offset = models.IntegerField(default=3, verbose_name="Смещение часового пояса",
                                      help_text="От -12 до +14, по умолчанию UTC+3 (Московское время)")
    is_content_manager = models.BooleanField(default=False, verbose_name="админ", )
    is_moderator = models.BooleanField(default=False, verbose_name="модератор", )

    is_banned = models.BooleanField(default=False, verbose_name="Забанен",)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.name} ({self.email})"


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь к которому относится токен",
                             help_text="токен для восстановления пароля", related_name="user_token")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания",
                                      help_text="введите дату создания токена")
    token = models.CharField(max_length=100, verbose_name="Token", **NULLABLE)
