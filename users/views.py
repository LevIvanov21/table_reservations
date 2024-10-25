import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.core.exceptions import PermissionDenied

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DetailView

from restaurant.models import ContentParameters
from restaurant.tasks import celery_send_mail
from restaurant.templates.restaurant.services import get_cached_booking_list, cache_clear
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User, UserToken
from users.services import get_password


class GetFormKwargsGetUserMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class GetFormClassUserIsOwnerMixin:
    def get_form_class(self):
        user = self.request.user
        if user.pk == self.kwargs.get("pk"):
            return UserProfileForm
        raise PermissionDenied


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token

        user_token = UserToken.objects.create(token=token, user=user)
        user_token.save()

        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        # print(url)
        # send_mail(
        #     subject="Подтверждение почты",
        #     message=f"Привет, перейди по ссылке для подтверждения почты {url}",
        #     from_email=EMAIL_HOST_USER,
        #     recipient_list=[user.email]
        # )
        subject = "Подтверждение почты",
        message = f"Привет, перейди по ссылке для подтверждения почты {url} ",

        email_list = []
        email_list.append(user.email)

        celery_send_mail.delay(subject, message, email_list)

        redirect_url = reverse("users:confirm_email", args=[user.email])
        self.success_url = redirect_url

        return super().form_valid(form)


def email_verification(request, token):
    this_user_token = get_object_or_404(UserToken, token=token)
    user = this_user_token.user

    try:
        confirm_timedelta = timezone.timedelta(minutes=ContentParameters.objects.get(title="confirm_timedelta"))
    except Exception:
        confirm_timedelta = timezone.timedelta(minutes=45)
        print("confirm_timedelta - установлено по умолчаеию (45 минут)")

    if this_user_token.created_at < timezone.now() - confirm_timedelta:
        user.delete()
        this_user_token.delete()
        return render(request, "users/token_expired.html")
    else:
        this_user_token.delete()
        user.is_active = True
        user.save()
        return render(request, "users/email_confirmed.html")


def token_expired(request):
    return render(request, "users/token_expired.html")


def email_confirmed(request):
    return render(request, "users/email_confirmed.html")


def confirm_email(request, email):
    try:
        confirm_timedelta = ContentParameters.objects.get(title="confirm_timedelta")
    except Exception:
        confirm_timedelta = 45
        print("confirm_timedelta - установлено по умолчанию (45 минут)")

    context = {
        "email": email, "confirm_timedelta": confirm_timedelta
    }

    return render(request, "users/confirm_email.html", context)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm

    def get_success_url(self):
        user_pk = self.request.user.pk
        return reverse("users:user_detail", kwargs={"pk": user_pk})

    def get_object(self, queryset=None):
        return self.request.user


class UserDetailView(LoginRequiredMixin, GetFormClassUserIsOwnerMixin, DetailView):
    model = User

    login_url = "users:login"
    redirect_field_name = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["booking_list"] = get_cached_booking_list().filter(user=self.object).order_by("date_field",
                                                                                              "time_start")
        user = self.request.user
        pk = self.kwargs.get("pk")

        if user.is_moderator or user.pk == pk:
            return context
        else:
            raise PermissionDenied


def password_recovery(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = get_object_or_404(User, email=email)

        password = get_password(12)

        message = f"Привет, держи новый сложный 12-ти символьный пароль, который ты тоже забудешь: {password} . \
                    Если вы не запрашивали восстановление пароля, просто игнорируйте это сообщение."

        # send_mail(
        #     subject="Восстановление пароля",
        #     message=message,
        #     from_email=EMAIL_HOST_USER,
        #     recipient_list=[email]
        # )
        subject = "Восстановление пароля",
        # message = f"Привет, перейди по ссылке для подтверждения почты {url} ",

        email_list = []
        email_list.append(email)

        celery_send_mail.delay(subject, message, email_list)

        user.set_password(password)
        user.save()
        return redirect(reverse("users:login"))

    return render(request, "users/password_recovery.html")


class CacheClearedLogoutView(LogoutView):

    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        cache_clear()
        return super().post(request, *args, **kwargs)


def cache_clear_when_login(request):
    # Ваш код обработки запроса
    # ...
    # Очистка кэша страницы
    cache_clear()
    return redirect(reverse("users:login"))
