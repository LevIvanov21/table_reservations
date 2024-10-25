import datetime
from django.test import TestCase

from restaurant.models import Table, Booking
from django.urls import reverse

from restaurant.templates.restaurant.services import cache_clear
from users.models import User


class QuestionsListViewTest(TestCase):
    fixtures = ["test_data.json"]

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/question_list/")
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("restaurant:question_list"))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("restaurant:question_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "restaurant/questions_list.html")

    def test_lists_resp_context(self):
        resp = self.client.get(reverse("restaurant:question_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("time_offset" in resp.context)
        self.assertTrue("questions_and_answers" in resp.context)
        self.assertTrue("time_offset" in resp.context)


class HomeListViewTest(TestCase):
    # CACHE_ENABLED = False
    # cache_clear()
    fixtures = ["test_data.json"]

    def setUp(self):
        self.CACHE_ENABLED = False
        cache_clear()

    def test_home_url_exists_at_desired_location(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_home_url_accessible_by_name(self):
        resp = self.client.get(reverse("restaurant:main"))
        self.assertEqual(resp.status_code, 200)

    def test_home_uses_correct_template(self):
        resp = self.client.get(reverse("restaurant:main"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "restaurant/home.html")

    def test_lists_resp_context(self):
        self.cache_off = False
        self.CACHE_ENABLED = False

        resp = self.client.get(reverse("restaurant:main"))
        self.assertEqual(resp.status_code, 200)

        self.assertTrue("home_about_inside1" in resp.context)
        self.assertTrue("home_about_inside2" in resp.context)
        self.assertTrue(resp.context["home_about"])
        self.assertTrue("home_food1" in resp.context)
        self.assertTrue("home_food2" in resp.context)
        self.assertTrue("home_food3" in resp.context)
        self.assertTrue("home_offer" in resp.context)
        self.assertTrue("telegram" in resp.context)
        self.assertTrue("home_adress" in resp.context)
        self.assertTrue("whatsup" in resp.context)
        self.assertTrue("vkontakte" in resp.context)


class AboutListViewTest(TestCase):
    # CACHE_ENABLED = False
    # cache_clear()
    fixtures = ["test_data.json"]

    def setUp(self):
        # self.cache_off = False
        self.CACHE_ENABLED = False
        cache_clear()

    def test_home_url_exists_at_desired_location(self):
        resp = self.client.get("/about_us/")
        self.assertEqual(resp.status_code, 200)

    def test_home_url_accessible_by_name(self):
        resp = self.client.get(reverse("restaurant:about_us"))
        self.assertEqual(resp.status_code, 200)

    def test_home_uses_correct_template(self):
        resp = self.client.get(reverse("restaurant:about_us"))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, "restaurant/about_us.html")

    def test_lists_resp_context(self):
        resp = self.client.get(reverse("restaurant:about_us"))
        self.assertEqual(resp.status_code, 200)

        self.assertTrue("about_us_mission_part" in resp.context)
        self.assertTrue("about_us_history_part1" in resp.context)
        self.assertTrue("about_us_history_part2" in resp.context)
        self.assertTrue("about_us_command_part1" in resp.context)
        self.assertTrue("about_us_command_part2" in resp.context)
        self.assertTrue("about_us_inside3" in resp.context)
        self.assertTrue("about_us_inside4" in resp.context)
        self.assertTrue("about_us_team1" in resp.context)
        self.assertTrue("about_us_team2" in resp.context)
        self.assertTrue("about_us_team3" in resp.context)


class BookingListViewTest(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        # Создание пользователя
        test_user_booking_list = User.objects.create_user(email="test_user_booking_list@test.ru", name="user1",
                                                          password="test")
        test_user_booking_list.save()

        # берем первый попавшийся столик из фикстуры
        table = Table.objects.first()

        # Создание 10 объектов Booking
        number_of_booking_copies = 10

        for i, booking in enumerate(range(number_of_booking_copies), start=1):
            date_next = datetime.date.today() + datetime.timedelta(days=1)
            time_next_1h = datetime.time((8 + i), 0, 0)
            time_next_2h = datetime.time((9 + i), 0, 0)

            booking = Booking.objects.create(user=test_user_booking_list, table=table, places=4,
                                             description="test_booking", notification=0, date_field=date_next,
                                             time_start=time_next_1h, time_end=time_next_2h, active=True)
            booking.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse("restaurant:booking_list"))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, "/users/login/?login=/booking_list/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(email="test_user_booking_list@test.ru", password="test")
        resp = self.client.get(reverse("restaurant:booking_list"))

        # Проверка что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), "user1 (test_user_booking_list@test.ru)")

        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, "restaurant/booking_list.html")

    def test_only_user_bookings_in_list(self):
        self.client.login(email="test_user_booking_list@test.ru", password="test")
        resp = self.client.get(reverse("restaurant:booking_list"))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), "user1 (test_user_booking_list@test.ru)")
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Проверка, что все бронирования пользователя показаны
        self.assertTrue("booking_list" in resp.context)
        self.assertEqual(len(resp.context["booking_list"]), 10)

        # Подтверждение, что все бронирования принадлежат testuser1
        for booking_item in resp.context["booking_list"]:
            self.assertEqual(resp.context["user"], booking_item.user)

        # проверка, что список отсортирован
        date_last = 0
        time_last = 0

        for copy in resp.context["booking_list"]:
            if date_last == 0:
                date_last = copy.date_field
                time_last = copy.time_start
            else:
                self.assertTrue(copy.date_field >= date_last)
                self.assertTrue(copy.time_start >= time_last)


class BookingCreateViewTest(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        # Создание пользователя
        test_user2 = User.objects.create_user(email="test_user2@test.ru", name="user2", password="test")
        test_user2.save()

        test_user1 = User.objects.create_user(email="test_user1@test.ru", name="user1", password="test")
        test_user1.save()

        # берем первый попавшийся столик из фикстуры
        table_1 = Table.objects.first()

        # берем первый попавшийся столик из фикстуры
        table_2 = Table.objects.last()

        # Создание 10 объектов Booking
        number_of_booking_copies = 10

        for i, booking in enumerate(range(number_of_booking_copies), start=1):
            date_next = datetime.date.today() + datetime.timedelta(days=2)
            time_next_1h = datetime.time((9 + i), 0, 0)
            time_next_2h = datetime.time((10 + i), 0, 0)

            booking = Booking.objects.create(user=test_user2, table=table_2, places=4, description="test_booking",
                                             notification=0,
                                             date_field=date_next, time_start=time_next_1h,
                                             time_end=time_next_2h, active=True)
            booking.save()
            booking = Booking.objects.create(user=test_user1, table=table_1, places=4, description="test_booking",
                                             notification=0,
                                             date_field=date_next, time_start=time_next_1h,
                                             time_end=time_next_2h, active=True)
            booking.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse("restaurant:booking_create"))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, "/users/login/?login=/booking_create/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(email="test_user2@test.ru", password="test")
        resp = self.client.get(reverse("restaurant:booking_create"))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), "user2 (test_user2@test.ru)")

        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, "restaurant/booking_form.html")

    def test_seeing_active_bookings_when_create(self):
        self.client.login(email="test_user2@test.ru", password="test")
        resp = self.client.get(reverse("restaurant:booking_create"))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), "user2 (test_user2@test.ru)")
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Проверка, что все бронирования пользователя показаны
        self.assertTrue("booking_list" in resp.context)
        self.assertEqual(len(resp.context["booking_list"]), 20)

        # Подтверждение, что бронирования принадлежат разным пользователям
        different_users = False
        for booking_item in resp.context["booking_list"]:
            if booking_item.user != resp.context["user"]:
                different_users = True
                break
        self.assertTrue(different_users)

        # проверка, что список отсортирован
        date_last = 0
        time_last = 0

        for copy in resp.context["booking_list"]:
            if date_last == 0:
                date_last = copy.date_field
                time_last = copy.time_start
            else:
                self.assertTrue(copy.date_field >= date_last)
                self.assertTrue(copy.time_start >= time_last)
