import datetime

from unittest import TestCase

from django.core.exceptions import ValidationError
from django.utils import timezone

from restaurant.forms import BookingForm, QuestionsForm, LimitedQuestionsForm
from restaurant.models import Table, Booking, BookingToken, ContentParameters
from restaurant.utils.utils import get_content_parameters
from users.models import User


class TestQuestionsForm(TestCase):

    def test_question_form_text_labels(self):
        form = QuestionsForm()
        self.assertTrue(form.fields["question_text"].label == "Текст вопроса")
        self.assertTrue(form.fields["sign"].label == "Подпись")
        self.assertTrue(form.fields["moderated"].label == "Проверен")
        self.assertTrue(form.fields["answer_text"].label == "Ответ на вопрос")

        with self.assertRaises(Exception):
            self.assertEqual(form.fields["created_at"].label, "введите дату создания")

    def test_question_form_help_texts(self):
        form = QuestionsForm()
        self.assertEqual(form.fields["question_text"].help_text, "Введите текст вопроса")
        self.assertEqual(form.fields["sign"].help_text, "Введите подпись под вопросом")
        self.assertEqual(form.fields["moderated"].help_text, "Введите признак проверки")
        self.assertEqual(form.fields["answer_text"].help_text, "Введите ответ на вопрос")

        with self.assertRaises(Exception):
            self.assertEqual(form.fields["created_at"].help_text, "введите дату создания")


class TestLimitedQuestionsForm(TestCase):

    def test_limited_question_form_text_labels(self):
        form = LimitedQuestionsForm()
        self.assertTrue(form.fields["question_text"].label == "Текст вопроса")
        self.assertTrue(form.fields["sign"].label == "Подпись")

        with self.assertRaises(Exception):
            self.assertFalse(form.fields["moderated"].label == "Проверен")
        with self.assertRaises(Exception):
            self.assertFalse(form.fields["answer_text"].label == "Ответ на вопрос")
        with self.assertRaises(Exception):
            self.assertFalse(form.fields["created_at"].label == "дата создания")

    def test_limited_question_form_help_texts(self):
        form = LimitedQuestionsForm()
        self.assertEqual(form.fields["question_text"].help_text, "Введите текст вопроса")
        self.assertEqual(form.fields["sign"].help_text, "Введите подпись под вопросом")


class TestBookingForm(TestCase):

    def test_booking_form_labels(self):
        form = BookingForm()

        self.assertTrue(form.fields["table"].label == "Столик")
        self.assertTrue(form.fields["places"].label == "Число бронируемых мест")
        self.assertTrue(form.fields["description"].label == "Примечания")
        self.assertTrue(form.fields["places"].label == "Число бронируемых мест")
        self.assertTrue(form.fields["notification"].label == "Оповещение на Telegram (если указан при регистрации)")
        self.assertTrue(form.fields["date_field"].label == "Дата бронирования")
        self.assertTrue(form.fields["time_start"].label == "Начало бронирования")
        self.assertTrue(form.fields["time_end"].label == "Конец бронирования")

        with self.assertRaises(Exception):
            self.assertTrue(form.fields["user"].label == "пользователь")
        with self.assertRaises(Exception):
            self.assertTrue(form.fields["active"])
        with self.assertRaises(Exception):
            self.assertTrue(form.fields["created_at"])

    def test_validate_date_time(self):
        parameters = {"period_of_booking": 14, "work_start": datetime.time(8, 0, 0),
                      "work_end": datetime.time(23, 0, 0), "confirm_timedelta": 45}

        date_out_period = datetime.date.today() + datetime.timedelta(weeks=4)

        date_past = datetime.date.today() - datetime.timedelta(days=2)
        date_next = datetime.date.today() + datetime.timedelta(days=1)

        time_next_1h = datetime.time(9, 0, 0)
        time_next_2h = datetime.time(12, 0, 0)

        correct_data = {"date_field": date_next, "time_start": time_next_1h, "time_end": time_next_2h}
        past_data = {"date_field": date_past, "time_start": time_next_1h, "time_end": time_next_2h}
        out_period = {"date_field": date_out_period, "time_start": time_next_1h, "time_end": time_next_2h}

        form_correct = BookingForm()
        form_correct.cleaned_data = correct_data

        form_past_d = BookingForm()
        form_past_d.cleaned_data = past_data

        form_out = BookingForm()
        form_out.cleaned_data = out_period

        before_open = {"date_field": date_next, "time_start": datetime.time(7, 0, 0),
                       "time_end": time_next_2h}
        after_close = {"date_field": date_next, "time_start": time_next_1h,
                       "time_end": datetime.time(23, 50, 0)}
        above_closing = {"date_field": date_next, "time_start": datetime.time(7, 0, 0),
                         "time_end": datetime.time(23, 50, 0)}

        form_after_close = BookingForm()
        form_after_close.cleaned_data = after_close

        form_before_open = BookingForm()
        form_before_open.cleaned_data = before_open

        form_above_closing = BookingForm()
        form_above_closing.cleaned_data = above_closing

        self.assertTrue(form_correct.validate_date_time(parameters))

        with self.assertRaises(Exception):
            form_past_d.validate_date_time(parameters)

        with self.assertRaises(ValidationError) as e:
            form_past_d.validate_date_time(parameters)
        self.assertEqual(e.exception.message, "Нельзя забронировать место на прошедшее время")

        with self.assertRaises(ValidationError) as e_3:
            form_out.validate_date_time(parameters)
        self.assertEqual(e_3.exception.message, f"Бронировать места можно не ранее чем за "
                                                f"{parameters.get('period_of_booking')} дней")

        with self.assertRaises(ValidationError) as e_4:
            form_after_close.validate_date_time(parameters)
        self.assertEqual(e_4.exception.message, "В это время (23:50) ресторан уже закрыт")

        with self.assertRaises(ValidationError) as e_5:
            form_before_open.validate_date_time(parameters)
        self.assertEqual(e_5.exception.message, "В это время (7:0) ресторан ещё не открылся")

        with self.assertRaises(ValidationError) as e_6:
            form_above_closing.validate_date_time(parameters)
        self.assertEqual(e_6.exception.message, "В это время (7:0) ресторан ещё не открылся")

    ...

    def test_clean_place(self):
        table = Table.objects.create(number=1, places=2, flour=1, description="test")

        correct_data = {"table": table, "places": 2}
        incorrect_data = {"table": table, "places": 10}
        incorrect_data_too = {"table": table, "places": 0}

        form_correct = BookingForm()
        form_correct.cleaned_data = correct_data

        form_incorrect = BookingForm()
        form_incorrect.cleaned_data = incorrect_data

        form_incorrect_too = BookingForm()
        form_incorrect_too.cleaned_data = incorrect_data_too

        self.assertTrue(form_correct.clean_place())

        with self.assertRaises(ValidationError) as e_1:
            form_incorrect.clean_place()
        self.assertEqual(e_1.exception.message,
                         f"За данным столиком всего {table.places} мест. "
                         f"Выберете столик с большим количеством мест "
                         f"или позже забронируйте соседний столик")

        with self.assertRaises(ValidationError) as e_2:
            form_incorrect_too.clean_place()
        self.assertEqual(e_2.exception.message, "Должно быть занято хотя бы одно место за столиком")

    def test_clean_table_active_table(self):
        user = User.objects.create_user(email="test@test.ru", password="test")

        # table с number = 1 уже есть
        table = Table.objects.create(number=2, places=6, flour=1, description="test")

        date_next = datetime.date.today() + datetime.timedelta(days=1)
        time_next_1h = datetime.time(9, 0, 0)
        time_next_2h = datetime.time(12, 0, 0)

        booking_active = Booking.objects.create(user=user, table=table, places=4, description="test", notification=0,
                                                date_field=date_next, time_start=time_next_1h,
                                                time_end=time_next_2h, active=True)
        booking_active.save()

        self.assertTrue(Booking.objects.all().count() > 0)
        time_border = timezone.now() - timezone.timedelta(minutes=45)

        correct_data = {"date_field": date_next, "time_start": datetime.time(14, 50, 0),
                        "time_end": datetime.time(16, 50, 0), "table": table}
        incorrect_data = {"date_field": date_next, "time_start": datetime.time(8, 50, 0),
                          "time_end": datetime.time(12, 20, 0), "table": table}
        incorrect_data_2 = {"date_field": date_next, "time_start": datetime.time(11, 50, 0),
                            "time_end": datetime.time(12, 20, 0), "table": table}
        incorrect_data_3 = {"date_field": date_next, "time_start": datetime.time(8, 50, 0),
                            "time_end": datetime.time(11, 50, 0), "table": table}

        form_correct = BookingForm()
        form_correct.cleaned_data = correct_data

        form_incorect = BookingForm()
        form_incorect.cleaned_data = incorrect_data
        text_err1 = "В указанный период времени столик забронирован"

        form_incorect_2 = BookingForm()
        form_incorect_2.cleaned_data = incorrect_data_2
        text_err2 = "В указанное время выбранный столик занят"

        form_incorect_3 = BookingForm()
        form_incorect_3.cleaned_data = incorrect_data_3
        text_err3 = "В указанное время выбранный столик еще не освободился"

        self.assertTrue(form_correct.clean_my_table(time_border))

        with self.assertRaises(ValidationError) as e_1:
            form_incorect.clean_my_table(time_border)
        self.assertEqual(e_1.exception.message, text_err1)

        with self.assertRaises(ValidationError) as e_2:
            form_incorect_2.clean_my_table(time_border)
        self.assertEqual(e_2.exception.message, text_err2)

        with self.assertRaises(ValidationError) as e_3:
            form_incorect_3.clean_my_table(time_border)
        self.assertEqual(e_3.exception.message, text_err3)

    def test_clean_table_wait_confirm_table(self):
        user = User.objects.create_user(email="test2@test.ru", password="test")

        # table с number = 1 уже есть
        table = Table.objects.create(number=3, places=2, flour=1, description="test")

        date_next = datetime.date.today() + datetime.timedelta(days=2)
        time_next_1h = datetime.time(9, 0, 0)
        time_next_2h = datetime.time(12, 0, 0)

        booking_inactive = Booking.objects.create(user=user, table=table, places=4, description="test", notification=0,
                                                  date_field=date_next, time_start=time_next_1h, time_end=time_next_2h,
                                                  active=False)

        token = BookingToken.objects.create(booking=booking_inactive, token="testtoken111500AAAAAaaaaaa!!!")
        token.save()
        booking_inactive.save()

        self.assertTrue(Booking.objects.all().count() > 0)
        time_border = timezone.now() - timezone.timedelta(minutes=1800)

        correct_data = {"date_field": date_next, "time_start": datetime.time(14, 50, 0),
                        "time_end": datetime.time(16, 50, 0), "table": table}
        incorrect_data = {"date_field": date_next, "time_start": datetime.time(8, 50, 0),
                          "time_end": datetime.time(12, 20, 0), "table": table}
        incorrect_data_2 = {"date_field": date_next, "time_start": datetime.time(11, 50, 0),
                            "time_end": datetime.time(12, 20, 0), "table": table}
        incorrect_data_3 = {"date_field": date_next, "time_start": datetime.time(8, 50, 0),
                            "time_end": datetime.time(11, 50, 0), "table": table}

        form_correct = BookingForm()
        form_correct.cleaned_data = correct_data

        form_incorect = BookingForm()
        form_incorect.cleaned_data = incorrect_data
        text_err1 = "В указанный период времени столик забронирован"

        form_incorect_2 = BookingForm()
        form_incorect_2.cleaned_data = incorrect_data_2
        text_err2 = "В указанное время выбранный столик занят"

        form_incorect_3 = BookingForm()
        form_incorect_3.cleaned_data = incorrect_data_3
        text_err3 = "В указанное время выбранный столик еще не освободился"

        self.assertTrue(form_correct.clean_my_table(time_border))

        with self.assertRaises(ValidationError) as e_1:
            form_incorect.clean_my_table(time_border)
        self.assertEqual(e_1.exception.message, text_err1)

        with self.assertRaises(ValidationError) as e_2:
            form_incorect_2.clean_my_table(time_border)
        self.assertEqual(e_2.exception.message, text_err2)

        with self.assertRaises(ValidationError) as e_3:
            form_incorect_3.clean_my_table(time_border)
        self.assertEqual(e_3.exception.message, text_err3)

    #
    def test_clean_table_deactivated_table(self):
        user = User.objects.create_user(email="test3@test.ru", password="test")

        # table с number = 1 уже есть
        table = Table.objects.create(number=4, places=6, flour=1, description="test")

        date_next = datetime.date.today() + datetime.timedelta(days=2)
        time_next_1h = datetime.time(9, 0, 0)
        time_next_2h = datetime.time(12, 0, 0)

        booking_inactive = Booking.objects.create(user=user, table=table, places=4, description="test", notification=0,
                                                  date_field=date_next, time_start=time_next_1h, time_end=time_next_2h,
                                                  active=False)
        booking_inactive.save()

        self.assertTrue(Booking.objects.all().count() > 0)
        time_border = timezone.now() - timezone.timedelta(minutes=1800)

        correct_data = {"date_field": date_next, "time_start": datetime.time(14, 50, 0),
                        "time_end": datetime.time(16, 50, 0), "table": table}
        incorrect_data = {"date_field": date_next, "time_start": datetime.time(8, 50, 0),
                          "time_end": datetime.time(12, 20, 0), "table": table}
        incorrect_data_2 = {"date_field": date_next, "time_start": datetime.time(11, 50, 0),
                            "time_end": datetime.time(12, 20, 0), "table": table}
        incorrect_data_3 = {"date_field": date_next, "time_start": datetime.time(8, 50, 0),
                            "time_end": datetime.time(11, 50, 0), "table": table}

        form_correct = BookingForm()
        form_correct.cleaned_data = correct_data

        form_incorect = BookingForm()
        form_incorect.cleaned_data = incorrect_data

        form_incorect_2 = BookingForm()
        form_incorect_2.cleaned_data = incorrect_data_2

        form_incorect_3 = BookingForm()
        form_incorect_3.cleaned_data = incorrect_data_3

        self.assertTrue(form_correct.clean_my_table(time_border))
        self.assertTrue(form_incorect.clean_my_table(time_border))
        self.assertTrue(form_incorect_2.clean_my_table(time_border))
        self.assertTrue(form_incorect_3.clean_my_table(time_border))

    #
    def test_clean_total(self):
        user = User.objects.create_user(email="test4@test.ru", password="test")
        table = Table.objects.create(number=5, places=6, flour=1, description="test")

        date_next = datetime.date.today() + datetime.timedelta(days=2)
        time_next_1h = datetime.time(9, 0, 0)
        time_next_2h = datetime.time(12, 0, 0)

        booking = Booking.objects.create(user=user, table=table, places=4, description="test", notification=0,
                                         date_field=date_next, time_start=time_next_1h, time_end=time_next_2h,
                                         active=True)
        booking.save()

        correct_data = {"date_field": date_next, "time_start": datetime.time(14, 50, 0),
                        "time_end": datetime.time(15, 50, 0), "table": table, "places": 4}

        form_correct = BookingForm()
        form_correct.cleaned_data = correct_data

        self.assertTrue(form_correct.clean())

    def test_content_parameters_get(self):
        content = ContentParameters.objects.all().delete()

        self.assertFalse(get_content_parameters(False))
        self.assertTrue(get_content_parameters(True))

        # а теперь не выбросит
        content = ContentParameters.objects.create(title="period_of_booking", body=10)
        content.save()
        content = ContentParameters.objects.create(title="work_start", body="12:00")
        content.save()
        content = ContentParameters.objects.create(title="work_end", body="16:00")
        content.save()
        content = ContentParameters.objects.create(title="confirm_timedelta", body=50)
        content.save()

        self.assertTrue(get_content_parameters(False))
