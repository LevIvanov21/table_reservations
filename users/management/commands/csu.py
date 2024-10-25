import os
from dotenv import load_dotenv
from django.core.management import BaseCommand
from users.models import User

load_dotenv()


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email="admin@sky.pro",
            first_name="Admin",
            last_name="SkyPro",
            is_staff=True,
            is_superuser=True,


        )

        psw_su = os.getenv("SUPERUSER_PSW")
        user.set_password(psw_su)
        user.save()

        user2 = User.objects.create(
            email="content-manager@sky.pro",
            first_name="Content-manager",
            last_name="SkyPro",
            is_staff=True,
            is_superuser=False,
        )
        psw_cm = os.getenv("CONTENT_MANAGER_PSW")
        user2.set_password(psw_cm)
        user2.save()
