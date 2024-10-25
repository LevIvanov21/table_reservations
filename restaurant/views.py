import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView

from restaurant.forms import BookingForm, QuestionsForm, LimitedQuestionsForm
from restaurant.models import Booking, Table, BookingToken, Questions

from dotenv import load_dotenv

from restaurant.tasks import celery_send_mail
from restaurant.templates.restaurant.services import get_cached_booking_list, get_cached_questions_list, \
    cache_delete_question_list, cache_delete_booking_list
from restaurant.utils.utils import get_content_text_from_postgres, \
    get_content_image_from_postgres, get_content_link_from_postgres, get_actual_bookings, get_content_parameters
from users.models import User

load_dotenv()

PARAMETERS = get_content_parameters(True)


class HomePageView(TemplateView):
    template_name = "restaurant/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # количество рассылок всего
        CONST1 = "home-about"
        CONST2 = "home-offer"
        CONST3 = "home-adress"

        context[CONST1.replace("-", "_")] = get_content_text_from_postgres(CONST1)
        context[CONST2.replace("-", "_")] = get_content_text_from_postgres(CONST2)
        context[CONST3.replace("-", "_")] = get_content_text_from_postgres(CONST3)

        IMGCONST1 = "home-about-inside1"
        IMGCONST2 = "home-about-inside2"
        IMGCONST3 = "home-food1"
        IMGCONST4 = "home-food2"
        IMGCONST5 = "home-food3"

        context[IMGCONST1.replace("-", "_")] = get_content_image_from_postgres(IMGCONST1)
        context[IMGCONST2.replace("-", "_")] = get_content_image_from_postgres(IMGCONST2)
        context[IMGCONST3.replace("-", "_")] = get_content_image_from_postgres(IMGCONST3)
        context[IMGCONST4.replace("-", "_")] = get_content_image_from_postgres(IMGCONST4)
        context[IMGCONST5.replace("-", "_")] = get_content_image_from_postgres(IMGCONST5)

        LINKCONST1 = "vkontakte"
        LINKCONST2 = "whatsup"
        LINKCONST3 = "telegram"

        context[LINKCONST1.replace("-", "_")] = get_content_link_from_postgres(LINKCONST1)
        context[LINKCONST2.replace("-", "_")] = get_content_link_from_postgres(LINKCONST2)
        context[LINKCONST3.replace("-", "_")] = get_content_link_from_postgres(LINKCONST3)

        return context


class AboutUsPageView(TemplateView):
    template_name = "restaurant/about_us.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # количество рассылок всего
        CONST1 = "about_us-mission-part"
        CONST2 = "about_us-history-part1"
        CONST3 = "about_us-history-part2"
        CONST4 = "about_us-command-part1"
        CONST5 = "about_us-command-part2"

        context[CONST1.replace("-", "_")] = get_content_text_from_postgres(CONST1)
        context[CONST2.replace("-", "_")] = get_content_text_from_postgres(CONST2)
        context[CONST3.replace("-", "_")] = get_content_text_from_postgres(CONST3)
        context[CONST4.replace("-", "_")] = get_content_text_from_postgres(CONST4)
        context[CONST5.replace("-", "_")] = get_content_text_from_postgres(CONST5)

        IMGCONST1 = "about_us-inside3"
        IMGCONST2 = "about_us-inside4"
        IMGCONST3 = "about_us-team1"
        IMGCONST4 = "about_us-team2"
        IMGCONST5 = "about_us-team3"

        context[IMGCONST1.replace("-", "_")] = get_content_image_from_postgres(IMGCONST1)
        context[IMGCONST2.replace("-", "_")] = get_content_image_from_postgres(IMGCONST2)
        context[IMGCONST3.replace("-", "_")] = get_content_image_from_postgres(IMGCONST3)
        context[IMGCONST4.replace("-", "_")] = get_content_image_from_postgres(IMGCONST4)
        context[IMGCONST5.replace("-", "_")] = get_content_image_from_postgres(IMGCONST5)

        return context


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    login_url = "users:login"
    redirect_field_name = "login"

    def get_success_url(self):
        return reverse("restaurant:booking_list")

    def form_valid(self, form):
        user = self.request.user
        if user == self.object.user or user.is_moderator:
            return
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # HAS_BEEN - реализация в будующем в настройках пользователя показывать ли прошедшие бронирования
        # # ONLY_USERS_PROPERTY - для обычных пользователей, админы смогут видеть все
        # context['only_users'] = os.getenv("ONLY_USERS_PROPERTY")
        context["has_been"] = True
        context["only_users"] = True

        context["time_offset"] = self.request.user.time_offset
        user = self.request.user
        context["user"] = user

        cashed_booking = get_cached_booking_list()

        # unfiltered_booking = cashed_booking.filter(user=user)
        context["booking_list"] = cashed_booking.filter(user=user).order_by("date_field", "time_start")

        return context


class Users:
    pass


class BookingCreateUpdateMixin:

    def form_valid(self, form):
        # Xозяином рассылки автоматически становится тот, кто её создал
        booking = form.save()
        user = self.request.user
        booking.user = user
        booking.active = False

        token = secrets.token_hex(16)
        # email = user.email

        booking.save()

        booking_token = BookingToken.objects.create(token=token, booking=booking)
        booking_token.save()

        host = self.request.get_host()
        url = f"http://{host}/booking_verification/{token}/"

        subject = "Подтверждение бронирования",
        message = f"Привет, перейди по ссылке для подтверждения бронирования: {url} ",
        # from_email = EMAIL_HOST_USER,
        # recipient_list = [email]

        # send_mail(
        #     subject="Подтверждение бронирования",
        #     message=f"Привет, перейди по ссылке для подтверждения бронирования: {url}",
        #     from_email=EMAIL_HOST_USER,
        #     recipient_list=[email]
        # )

        email_list = []
        # email_list.append(user.email)

        subscriptions = User.objects.filter(pk=self.request.user.pk)
        for s in subscriptions:
            email_list.append(s.email)

        # The values_list() method returns a QuerySet containing tuples: <QuerySet [(1,), (2,)]>
        # values_list() with a single field, use flat=True to return a QuerySet instead of 1-tuples: <QuerySet [1, 2]>
        # email_list = subscriptions.values_list("email", flat=True)
        celery_send_mail.delay(subject, message, email_list)

        get_cached_booking_list(recached=True)
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        email = user.email
        return reverse("restaurant:confirm_booking", args=[email])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # получение времени подтверждения бронирования, получение времени, которое определяет границу регистрации

        confirm_timedelta = timezone.timedelta(minutes=PARAMETERS.get("confirm_timedelta"))

        # try:
        #
        #     confirm_timedelta = timezone.timedelta(
        #         minutes=ContentParameters.objects.get(title="confirm_timedelta"))
        #
        #     confirm_timedelta = timezone.timedelta(
        #         minutes=ContentParameters.objects.get(title="confirm_timedelta"))
        # except Exception:
        #     confirm_timedelta = timezone.timedelta(minutes=45)

        time_border = timezone.now() - confirm_timedelta

        # список pk бронирований, которые могут быть подтверждены

        # отбор по времени конца бронирования без учета активности:
        present_time_booking = get_actual_bookings(active=False, time_start=False)
        # время подтверждения не истекло у следующих pk
        booking_tokens = [token.booking.pk for token in BookingToken.objects.filter(created_at__gt=time_border)]
        # теперь фильтруем по pk исключая те, которые не были подтверждены
        # получение списка актуальных бронирований
        bookings = present_time_booking.filter(Q(active=True) | Q(pk__in=booking_tokens)).order_by(
            "date_field", "time_start")

        # получение списка задействованных столиков
        table_pk = [b.table.pk for b in bookings]
        tables = Table.objects.filter(pk__in=table_pk).order_by("number")

        context["tables_list"] = tables
        context["booking_list"] = bookings

        context["period_of_booking"] = PARAMETERS.get("period_of_booking")
        context["work_start"] = PARAMETERS.get("work_start")
        context["work_end"] = PARAMETERS.get("work_end")

        CONST1 = "booking_create"
        context[CONST1.replace("-", "_")] = get_content_text_from_postgres(CONST1)

        return context


def confirm_booking(request, email):

    confirm_timedelta = timezone.timedelta(minutes=PARAMETERS.get("confirm_timedelta"))
    context = {
        "email": email, "confirm_timedelta": confirm_timedelta
    }
    return render(request, "restaurant/confirm_booking.html", context)


def booking_verification(request, token):
    this_booking_token = get_object_or_404(BookingToken, token=token)
    booking = this_booking_token.booking

    # try:
    #     confirm_timedelta_raw = ContentParameters.objects.get(title="confirm_timedelta")
    #     # confirm_timedelta = timezone.timedelta(minutes=ContentParameters.objects.get(title="confirm_timedelta"))
    # except Exception:
    #     confirm_timedelta_raw = timezone.timedelta(minutes=45)
    confirm_timedelta = timezone.timedelta(minutes=PARAMETERS.get("confirm_timedelta"))
    # confirm_timedelta = timezone.timedelta(minutes=int(confirm_timedelta_raw.body))

    if this_booking_token.created_at < timezone.now() - confirm_timedelta:
        booking.delete()
        this_booking_token.delete()
        get_cached_booking_list(recached=True)
        return render(request, "restaurant/token_expired.html")
    else:
        this_booking_token.delete()
        booking.active = True
        booking.save()
        get_cached_booking_list(recached=True)
        return render(request, "restaurant/booking_confirmed.html")


def token_expired(request):
    return render(request, "restaurant/token_expired.html")


def email_confirmed(request):
    return render(request, "restaurant/booking_confirmed.html")


class BookingCreateView(LoginRequiredMixin, BookingCreateUpdateMixin, CreateView):
    model = Booking
    form_class = BookingForm
    login_url = "users:login"
    redirect_field_name = "login"


class BookingUpdateView(LoginRequiredMixin, BookingCreateUpdateMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    login_url = "users:login"
    redirect_field_name = "login"

    def get_form_class(self):
        user = self.request.user
        if user == self.object.user:
            return BookingForm
        raise PermissionDenied


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    login_url = "users:login"
    redirect_field_name = "login"

    def get_success_url(self):
        # user_pk = self.request.user.pk
        return reverse("restaurant:booking_list")

    def form_valid(self, form):

        user = self.request.user
        if user == self.object.user:
            cache_delete_booking_list()
            # get_cached_booking_list(recached=True)
            return super().form_valid(form)
        else:
            raise PermissionDenied


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    login_url = "users:login"
    redirect_field_name = "login"

    def form_valid(self, form):
        user = self.request.user
        if user == self.object.user or user.is_moderator:
            # cashed_booking = get_cached_booking_list()
            #
            # # unfiltered_booking = cashed_booking.filter(user=user)
            # # context["object"] = cashed_booking.filter(user=user).order_by("date_field", "time_start")
            #
            # # get_cached_booking_list()
            return super().form_valid(form)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = get_cached_booking_list().get(id=self.kwargs.get("pk"))
        return context


def toggle_activity_booking(request, pk):
    booking_item = get_object_or_404(Booking, pk=pk)
    if booking_item.active:
        booking_item.active = False
    booking_item.save()

    get_cached_booking_list(recached=True)
    return redirect(reverse("restaurant:booking_list"))


class QuestionListView(ListView):
    model = Questions

    login_url = "users:login"
    redirect_field_name = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        CONST1 = "questions_and_answers"
        context[CONST1.replace("-", "_")] = get_content_text_from_postgres(CONST1)

        cashed_questions = get_cached_questions_list()
        context["object_list"] = cashed_questions

        user = self.request.user
        try:
            context["time_offset"] = user.time_offset
        except Exception:
            context["time_offset"] = 0

        return context


class QuestionCreateView(CreateView):
    model = Questions

    def get_form_class(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return QuestionsForm
        else:
            return LimitedQuestionsForm

    def form_valid(self, form):

        questions_list = form.save()
        questions_list.save()
        get_cached_questions_list(recached=True)
        return super().form_valid(form)

    def get_success_url(self):

        user = self.request.user
        if user.is_superuser or user.is_staff:
            return reverse("restaurant:question_list")
        else:
            return reverse("restaurant:questions_success", args=["question_premoderated"])


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Questions
    form_class = QuestionsForm
    login_url = "users:login"
    redirect_field_name = "login"
    success_url = reverse_lazy("restaurant:question_list")

    def form_valid(self, form):
        questions_list = form.save()
        questions_list.save()
        get_cached_questions_list(recached=True)
        return super().form_valid(form)


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Questions
    login_url = "users:login"
    redirect_field_name = "login"
    success_url = reverse_lazy("restaurant:question_list")

    def form_valid(self, form):
        cache_delete_question_list()

        return super().form_valid(form)


def questions_success(request, message):
    context = {
        "message": get_content_text_from_postgres(message),
    }
    return render(request, "restaurant/questions_success.html", context)
