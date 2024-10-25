from django.test import TestCase
from users.models import User, UserToken


class UserTest(TestCase):
    # fixtures = ['test_data.json']

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(email="test_user@test.ru", name="user", password="test")
        test_user.save()

    def test_user_labels(self):
        test_user = User.objects.get(email="test_user@test.ru")

        email_label = test_user._meta.get_field("email").verbose_name
        name_label = test_user._meta.get_field("name").verbose_name
        description_label = test_user._meta.get_field("description").verbose_name
        phone_number_label = test_user._meta.get_field("phone_number").verbose_name
        avatar_label = test_user._meta.get_field("avatar").verbose_name
        tg_nick_label = test_user._meta.get_field("tg_nick").verbose_name
        tg_chat_id_label = test_user._meta.get_field("tg_chat_id").verbose_name
        time_offset_label = test_user._meta.get_field("time_offset").verbose_name

        self.assertEqual(email_label, "почта")
        self.assertEqual(name_label, "имя пользователя")
        self.assertEqual(description_label, "описание")
        self.assertEqual(phone_number_label, "телефон")
        self.assertEqual(avatar_label, "аватар")
        self.assertEqual(tg_nick_label, "Tg name")
        self.assertEqual(tg_chat_id_label, "Телеграм chat-id")
        self.assertEqual(time_offset_label, "Смещение часового пояса")

    def test_review_sign_max_length(self):
        test_user = User.objects.get(email="test_user@test.ru")

        email_length = test_user._meta.get_field("email").max_length
        name_length = test_user._meta.get_field("name").max_length
        tg_nick_length = test_user._meta.get_field("tg_nick").max_length
        tg_chat_id_length = test_user._meta.get_field("tg_chat_id").max_length

        self.assertEqual(email_length, 150)
        self.assertEqual(name_length, 150)
        self.assertEqual(tg_nick_length, 50)
        self.assertEqual(tg_chat_id_length, 50)

    def test_review_str(self):
        user = User.objects.get(email="test_user@test.ru")
        expected_object_name = f"{user.name} ({user.email})"
        self.assertEqual(expected_object_name, str(user))


class UserTokenTest(TestCase):
    # fixtures = ['test_data.json']

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(email="test_user@test.ru", name="user", password="test")
        test_user.save()

        token = UserToken.objects.create(user=test_user, token="test_token")
        token.save()

    def test_user_token_label(self):
        test_user = User.objects.get(email="test_user@test.ru")
        token = UserToken.objects.get(user=test_user)

        user_label = token._meta.get_field("user").verbose_name
        self.assertEqual(user_label, "пользователь к которому относится токен")

        token_label = token._meta.get_field("token").verbose_name
        self.assertEqual(token_label, "Token")

        created_at_label = token._meta.get_field("created_at").verbose_name
        self.assertEqual(created_at_label, "дата создания")

    def test_user_token_max_length(self):
        test_user = User.objects.get(email="test_user@test.ru")
        token = UserToken.objects.get(user=test_user)

        token_length = token._meta.get_field("token").max_length
        self.assertEqual(token_length, 100)
