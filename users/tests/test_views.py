import datetime

from django.test import TestCase

from restaurant.models import Booking, Table
from users.models import User
from django.urls import reverse


class RegisterViewTest(TestCase):
    def test_home_url_exists_at_desired_location(self):
        resp = self.client.get("/users/register/")
        self.assertEqual(resp.status_code, 200)

    def test_home_url_accessible_by_name(self):
        resp = self.client.get(reverse("users:register"))
        self.assertEqual(resp.status_code, 200)

    def test_home_uses_correct_template(self):
        resp = self.client.get(reverse("users:register"))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, "users/register.html")


class UserProfileViewTest(TestCase):
    def setUp(self):

        # Создание ользователя
        test_user_profile = User.objects.create_user(email="test_user_profile@test.ru", name="user1", password="test")
        test_user_profile.save()

    def test_logged_in_uses_correct_template(self):
        self.client.login(email="test_user_profile@test.ru", password="test")
        resp = self.client.get(reverse("users:profile"))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), "user1 (test_user_profile@test.ru)")

        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, "users/user_form.html")


class UserDetailViewTest(TestCase):
    def setUp(self):

        # Создание ользователя
        test_user_detail = User.objects.create_user(email="test_user_detail@test.ru", name="user1", password="test")
        test_user_detail.save()

        # берем первый попавшийся столик из фикстуры
        table = Table.objects.create(number=1, places=2, flour=1, description="test")
        table.save()

        # Создание 10 объектов Booking
        number_of_booking_copies = 10

        for i, booking in enumerate(range(number_of_booking_copies), start=1):
            date_next = datetime.date.today() + datetime.timedelta(days=1)
            time_next_1h = datetime.time((8 + i), 0, 0)
            time_next_2h = datetime.time((9 + i), 0, 0)

            booking = Booking.objects.create(user=test_user_detail, table=table, places=4, description="test_booking",
                                             notification=0,
                                             date_field=date_next, time_start=time_next_1h,
                                             time_end=time_next_2h, active=True)
            booking.save()

    def test_logged_in_uses_correct_template(self):

        user_pk = User.objects.get(email="test_user_detail@test.ru").pk

        self.client.login(email="test_user_detail@test.ru", password="test")
        resp = self.client.get(reverse("users:user_detail", kwargs={"pk": user_pk}))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), "user1 (test_user_detail@test.ru)")

        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, "users/user_detail.html")

        # Проверка, что все бронирования пользователя показаны
        self.assertTrue("booking_list" in resp.context)
        self.assertEqual(len(resp.context["booking_list"]), 10)

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
