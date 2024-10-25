from django.test import TestCase
from restaurant.models import Questions, Table, Booking, BookingToken, Contentlink, ContentParameters, ContentImage, \
    ContentText, Review
from users.models import User


class RevewTest(TestCase):
    fixtures = ["test_data.json"]

    @classmethod
    def setUpTestData(cls):
        user = User.objects.first()
        Review.objects.create(review_text="test", author=user, sign=user.email, grade=5, moderated=True,
                              answer_text="test")

    def test_review_review_text_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("author").verbose_name
        self.assertEqual(field_label, "пользователь")

    def test_review_review_field_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("review_text").verbose_name
        self.assertEqual(field_label, "Текст отзыва")

    def test_review_sign_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("sign").verbose_name
        self.assertEqual(field_label, "Подпись")

    def test_review_sign_max_length(self):
        review = Review.objects.first()
        max_length = review._meta.get_field("sign").max_length
        self.assertEqual(max_length, 50)

    def test_review_grade_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("grade").verbose_name
        self.assertEqual(field_label, "Оценка")

    def test_review_moderated_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("moderated").verbose_name
        self.assertEqual(field_label, "Проверен")

    def test_review_answer_text_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("answer_text").verbose_name
        self.assertEqual(field_label, "Ответ на отзыв")

    def test_review_created_at_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("created_at").verbose_name
        self.assertEqual(field_label, "дата создания")

    def test_review_updated_at_label(self):
        review = Review.objects.first()
        field_label = review._meta.get_field("updated_at").verbose_name
        self.assertEqual(field_label, "дата изменения")

    def test_review_str(self):
        review = Review.objects.first()
        expected_object_name = f"{review.grade} - {review.sign}"
        self.assertEqual(expected_object_name, str(review))


class ContentTextTest(TestCase):
    fixtures = ["test_data.json"]

    def test_content_text_title_label(self):
        content_text = ContentText.objects.first()
        field_label = content_text._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "контент-название")

    def test_content_text_title_help_text(self):
        content_text = ContentText.objects.first()
        field_label = content_text._meta.get_field("title").help_text
        self.assertEqual(field_label, "введите название текстового блока")

    def test_content_text_title_max_length(self):
        content_text = ContentText.objects.first()
        max_length = content_text._meta.get_field("title").max_length
        self.assertEqual(max_length, 150)

    def test_content_text_body_label(self):
        content_text = ContentText.objects.first()
        field_label = content_text._meta.get_field("body").verbose_name
        self.assertEqual(field_label, "тело текстового блока")

    def test_content_text_body_help_text(self):
        content_text = ContentText.objects.first()
        field_label = content_text._meta.get_field("body").help_text
        self.assertEqual(field_label, "введите тело текстового блока")

    def test_content_text_str(self):
        content_text = ContentText.objects.first()
        expected_object_name = f"{content_text.title}: {content_text.body}"
        self.assertEqual(expected_object_name, str(content_text))


class ContentImageTest(TestCase):
    fixtures = ["test_data.json"]

    def test_content_image_title_label(self):
        content_image = ContentImage.objects.first()
        field_label = content_image._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "картинка-название")

    def test_content_image_title_max_length(self):
        content_image = ContentImage.objects.first()
        max_length = content_image._meta.get_field("title").max_length
        self.assertEqual(max_length, 150)

    def test_content_image_description_label(self):
        content_image = ContentImage.objects.first()
        field_label = content_image._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "Описание картинки")

    def test_content_image_description_help_text(self):
        content_image = ContentImage.objects.first()
        field_label = content_image._meta.get_field("description").help_text
        self.assertEqual(field_label, "Введите описание картинки")

    def test_content_image_image_label(self):
        content_image = ContentImage.objects.first()
        field_label = content_image._meta.get_field("image").verbose_name
        self.assertEqual(field_label, "Изображение")

    def test_content_image_str(self):
        content_image = ContentImage.objects.first()
        expected_object_name = f"{content_image.title}: {content_image.description}"
        self.assertEqual(expected_object_name, str(content_image))


class ContentParametersTest(TestCase):
    fixtures = ["test_data.json"]

    def test_content_parameters_title_label(self):
        content_parameters = ContentParameters.objects.first()
        field_label = content_parameters._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "название параметра")

    def test_content_parameters_title_max_length(self):
        content_parameters = ContentParameters.objects.first()
        max_length = content_parameters._meta.get_field("title").max_length
        self.assertEqual(max_length, 50)

    def test_content_parameters_body_label(self):
        content_parameters = ContentParameters.objects.first()
        field_label = content_parameters._meta.get_field("body").verbose_name
        self.assertEqual(field_label, "значение параметра")

    def test_content_parameters_body_max_length(self):
        content_parameters = ContentParameters.objects.first()
        max_length = content_parameters._meta.get_field("body").max_length
        self.assertEqual(max_length, 150)

    def test_content_parameters_description_label(self):
        content_parameters = ContentParameters.objects.first()
        field_label = content_parameters._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "описание параметра")

    def test_content_parameters_str(self):
        content_parameters = ContentParameters.objects.first()
        expected_object_name = f"{content_parameters.body}"
        self.assertEqual(expected_object_name, str(content_parameters))


class ContentlinkTest(TestCase):
    fixtures = ["test_data.json"]

    def test_content_link_title_label(self):
        content_link = Contentlink.objects.first()
        field_label = content_link._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "название ссылки")

    def test_content_link_title_max_length(self):
        content_link = Contentlink.objects.first()
        max_length = content_link._meta.get_field("title").max_length
        self.assertEqual(max_length, 50)

    def test_content_link_text_label(self):
        content_link = Contentlink.objects.first()
        field_label = content_link._meta.get_field("text").verbose_name
        self.assertEqual(field_label, "текст ссылки")

    def test_content_link_text_max_length(self):
        content_link = Contentlink.objects.first()
        max_length = content_link._meta.get_field("text").max_length
        self.assertEqual(max_length, 50)

    def test_content_link_description_label(self):
        content_link = Contentlink.objects.first()
        field_label = content_link._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "описание ссылки")

    def test_content_link_link_label(self):
        content_link = Contentlink.objects.first()
        field_label = content_link._meta.get_field("link").verbose_name
        self.assertEqual(field_label, "адрес ссылки")

    def test_content_link_link_max_length(self):
        content_link = Contentlink.objects.first()
        max_length = content_link._meta.get_field("link").max_length
        self.assertEqual(max_length, 150)

    def test_content_link_str(self):
        content_link = Contentlink.objects.first()
        expected_object_name = f"{content_link.link}"
        self.assertEqual(expected_object_name, str(content_link))


class BookingTokenTest(TestCase):
    fixtures = ["test_data.json"]

    @classmethod
    def setUpTestData(cls):
        booking = Booking.objects.first()
        BookingToken.objects.create(booking=booking, token="test_token")

    def test_booking_token_booking_label(self):
        obj = BookingToken.objects.first()
        field_label = obj._meta.get_field("booking").verbose_name
        self.assertEqual(field_label, "бронирование")

    def test_booking_token_created_at_label(self):
        obj = BookingToken.objects.first()
        field_label = obj._meta.get_field("created_at").verbose_name
        self.assertEqual(field_label, "дата создания")

    def test_booking_token_token_label(self):
        obj = BookingToken.objects.first()
        field_label = obj._meta.get_field("token").verbose_name
        self.assertEqual(field_label, "Token")

    def test_booking_token_token_max_length(self):
        obj = BookingToken.objects.get(id=1)
        max_length = obj._meta.get_field("token").max_length
        self.assertEqual(max_length, 100)


class BookingModelTest(TestCase):
    fixtures = ["test_data.json"]

    def test_booking_user_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("user").verbose_name
        self.assertEqual(field_label, "пользователь")

    def test_booking_table_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("table").verbose_name
        self.assertEqual(field_label, "столик")

    def test_booking_places_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("places").verbose_name
        self.assertEqual(field_label, "Число бронируемых мест")

    def test_booking_description_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "Примечания")

    def test_booking_notification_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("notification").verbose_name
        self.assertEqual(field_label, "Оповещение на Telegram (если указан при регистрации)")

    def test_booking_date_field_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("date_field").verbose_name
        self.assertEqual(field_label, "дата бронирования")

    def test_booking_time_start_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("time_start").verbose_name
        self.assertEqual(field_label, "начало бронирования")

    def test_booking_time_end_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("time_end").verbose_name
        self.assertEqual(field_label, "конец бронирования")

    def test_booking_active_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("active").verbose_name
        self.assertEqual(field_label, "активно ли бронирование")

    def test_booking_created_at_label(self):
        booking = Booking.objects.first()
        field_label = booking._meta.get_field("created_at").verbose_name
        self.assertEqual(field_label, "дата создания")

    def test_booking_str(self):
        booking = Booking.objects.first()
        expected_object_name = f"{booking.pk}, {booking.user} - {booking.table}"
        self.assertEqual(expected_object_name, str(booking))


class TableModelTest(TestCase):
    fixtures = ["test_data.json"]

    def test_table_number_label(self):
        table = Table.objects.get(id=1)
        field_label = table._meta.get_field("number").verbose_name
        self.assertEqual(field_label, "Номер столика")

    def test_table_places_label(self):
        table = Table.objects.get(id=1)
        field_label = table._meta.get_field("places").verbose_name
        self.assertEqual(field_label, "Число сидячих мест у столика")

    def test_table_flour_label(self):
        table = Table.objects.get(id=1)
        field_label = table._meta.get_field("flour").verbose_name
        self.assertEqual(field_label, "Этаж нахождения столика")

    def test_table_description_label(self):
        table = Table.objects.get(id=1)
        field_label = table._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "Описание столика")

    def test_table_str(self):
        table = Table.objects.get(id=1)
        expected_object_name = f"cтолик {table.number}"
        self.assertEqual(expected_object_name, str(table))


class QuestionsModelTest(TestCase):
    fixtures = ["test_data.json"]

    @classmethod
    def setUpTestData(cls):
        Questions.objects.create(question_text="test_question_text", sign="test_sign", moderated=True,
                                 answer_text="answer_text_test")

    def test_question_text_label(self):
        question = Questions.objects.get(id=1)
        field_label = question._meta.get_field("question_text").verbose_name
        self.assertEqual(field_label, "Текст вопроса")

    def test_moderated_label(self):
        question = Questions.objects.get(id=1)
        field_label = question._meta.get_field("moderated").verbose_name
        self.assertEqual(field_label, "Проверен")

    def test_answer_text_label(self):
        question = Questions.objects.get(id=1)
        field_label = question._meta.get_field("answer_text").verbose_name
        self.assertEqual(field_label, "Ответ на вопрос")

    def test_created_at_label(self):
        question = Questions.objects.get(id=1)
        field_label = question._meta.get_field("created_at").verbose_name
        self.assertEqual(field_label, "дата создания")

    def test_sign_label(self):
        question = Questions.objects.get(id=1)
        field_label = question._meta.get_field("sign").verbose_name
        self.assertEqual(field_label, "Подпись")

    def test_sign_max_length(self):
        question = Questions.objects.get(id=1)
        max_length = question._meta.get_field("sign").max_length
        self.assertEqual(max_length, 50)

    def test_question_str(self):
        question = Questions.objects.get(id=1)
        expected_object_name = "%s" % (question.question_text)
        self.assertEqual(expected_object_name, str(question))
