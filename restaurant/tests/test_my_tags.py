from datetime import datetime, timedelta, time


from unittest import TestCase

from restaurant.templatetags.my_tags import current_time, time_to_local, has_been, \
    generate_fake_mail, last_five_contacts, media_filter, user_media_filter


class UtilsTest(TestCase):
    def test_current_time(self):
        string_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.assertEqual(current_time("%d/%m/%Y, %H:%M:%S"), string_time)

    def test_time_to_local(self):
        dt = datetime.now()
        self.assertEqual(time_to_local(dt, 3), dt + timedelta(hours=3))

    def test_has_been(self):
        dt_past = (datetime.now() - timedelta(days=3))
        dt_next = (datetime.now() + timedelta(days=3))

        simple_time = time(9, 0, 0)

        self.assertTrue(has_been(dt_past, simple_time))
        self.assertFalse(has_been(dt_next, simple_time))

    def test_generate_fake_mail(self):
        self.assertTrue("@" in str(generate_fake_mail(10)))

    def test_last_five_contacts(self):
        self.assertEqual(last_five_contacts([1, 2, 3, 4, 5, 6, 7]), [3, 4, 5, 6, 7])

    def test_media_filter(self):
        self.assertEqual(media_filter(None), "/static/image/no_image.png")
        self.assertEqual(media_filter("test.png"), "/media/test.png")

    def test_user_media_filter(self):
        self.assertEqual(user_media_filter(None), "/static/image/no_avatar.png")
        self.assertEqual(user_media_filter("test.png"), "/media/test.png")
