from django.core.management.base import BaseCommand
import os
from authentication.models import CustomUser


class Command(BaseCommand):
    help = "Create a superuser if none exists (for Render deployment)"

    def handle(self, *args, **kwargs):
        try:
            email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
            password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")
            first_name = os.getenv("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
            last_name = os.getenv("DJANGO_SUPERUSER_LAST_NAME", "User")
            phone_no = os.getenv("DJANGO_SUPERUSER_PHONE", "0000000000")

            if not CustomUser.objects.filter(email=email).exists():
                CustomUser.objects.create_superuser(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_no=phone_no,
                    password=password,
                )
                self.stdout.write(self.style.SUCCESS(f"Superuser {email} created"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Superuser {email} already exists")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating superuser: {e}"))
