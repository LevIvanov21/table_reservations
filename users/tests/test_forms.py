from django.core.exceptions import ValidationError
from django.test import TestCase
from users.forms import UserRegisterForm, UserProfileForm


class TestUserRegisterForm(TestCase):
    def test_user_registered_form_labels(self):
        form = UserRegisterForm()
        self.assertTrue(form.fields["email"].label == "Почта")
        self.assertTrue(form.fields["name"].label == "Имя пользователя")

    def test_question_form_help_texts(self):
        form = UserRegisterForm()
        self.assertEqual(form.fields["email"].help_text, "Введите вашу почту")
        self.assertEqual(form.fields["name"].help_text, "Введите ваше имя")


class TestUserProfileForm(TestCase):

    def test_user_profile_form_labels(self):
        form = UserProfileForm()

        self.assertTrue(form.fields["email"].label == "Почта")
        self.assertTrue(form.fields["name"].label == "Имя пользователя")

        self.assertTrue(form.fields["description"].label == "Описание")
        self.assertTrue(form.fields["phone_number"].label == "Телефон")
        self.assertTrue(form.fields["avatar"].label == "Аватар")
        self.assertTrue(form.fields["tg_nick"].label == "Tg name")
        self.assertTrue(form.fields["tg_chat_id"].label == "Телеграм chat-id")
        self.assertTrue(form.fields["time_offset"].label == "Смещение часового пояса")

    def test_user_profile_form_clean(self):
        correct_data = {"time_offset": 3}
        incorrect_data = {"time_offset": -13}
        incorrect_data_too = {"time_offset": 15}

        form_correct = UserProfileForm()
        form_correct.cleaned_data = correct_data

        form_incorrect = UserProfileForm()
        form_incorrect.cleaned_data = incorrect_data

        form_incorrect_too = UserProfileForm()
        form_incorrect_too.cleaned_data = incorrect_data_too

        self.assertTrue(form_correct.clean())

        with self.assertRaises(ValidationError) as e_1:
            form_incorrect.clean()
        self.assertEqual(e_1.exception.message, "Невозможное смещение часового пояса: -13 часа")

        with self.assertRaises(ValidationError) as e_2:
            form_incorrect_too.clean()
        self.assertEqual(e_2.exception.message, "Невозможное смещение часового пояса: 15 часа")
