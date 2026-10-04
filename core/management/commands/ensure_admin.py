import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée ou met à jour le compte administrateur à partir des variables DJANGO_SUPERUSER_*."

    def handle(self, *args, **opts):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not username or not password:
            self.stdout.write("Variables DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD absentes : rien à faire.")
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": os.environ.get("DJANGO_SUPERUSER_EMAIL", "")})
        user.is_staff = user.is_superuser = user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(f"Administrateur '{username}' {'créé' if created else 'mis à jour'}.")
