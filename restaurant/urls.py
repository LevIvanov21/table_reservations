from django.urls import path
from django.views.decorators.cache import cache_page

from .views import HomePageView, AboutUsPageView, BookingListView, BookingCreateView, BookingUpdateView, \
    BookingDeleteView, BookingDetailView, toggle_activity_booking, confirm_booking, booking_verification, \
    QuestionCreateView, QuestionListView, QuestionUpdateView, QuestionDeleteView, questions_success

# MessageCreateView,

from restaurant.apps import RestaurantConfig

app_name = RestaurantConfig.name

urlpatterns = [
    # path("actual_booking/", actual_booking, name="actual_booking"),

    # страницы вообще почти не меняются, потому закеширую их на 300 секунд (5 минут!)
    # изменение параметров страницы (текст и картинки) будут конечно отражаться на сайте с 5 минутной задержкой
    # не вижу в этом проблемы, они меняются так редко что можно и подождать
    path("", cache_page(300)(HomePageView.as_view()), name="main"),
    path("about_us/", cache_page(300)(AboutUsPageView.as_view()), name="about_us"),

    path("booking_list/", BookingListView.as_view(), name="booking_list"),
    path("booking_create/", BookingCreateView.as_view(), name="booking_create"),
    path("booking_update/<int:pk>/", BookingUpdateView.as_view(), name="booking_update"),
    path("booking_delete/<int:pk>/", BookingDeleteView.as_view(), name="booking_delete"),
    path("booking_detail/<int:pk>/", BookingDetailView.as_view(), name="booking_detail"),

    path("booking_activity/<int:pk>/", toggle_activity_booking, name="booking_activity"),

    path("confirm_booking/<str:email>/", confirm_booking, name="confirm_booking"),
    path("booking_verification/<str:token>/", booking_verification, name="booking_verification"),

    path("token_expired/", booking_verification, name="token_expired"),
    path("booking_confirmed/", booking_verification, name="booking_confirmed"),
    # question
    path("question_create/", QuestionCreateView.as_view(), name="question_create"),
    path("question_update/<int:pk>/", QuestionUpdateView.as_view(), name="question_update"),
    path("question_delete/<int:pk>/", QuestionDeleteView.as_view(), name="question_delete"),
    path("question_list/", QuestionListView.as_view(), name="question_list"),
    path("question_success/<str:message>/", questions_success, name="questions_success"),
]
