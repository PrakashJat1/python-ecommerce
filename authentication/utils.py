import random
from django.core.mail import EmailMultiAlternatives
from django_otp.oath import hotp
from typing import List
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .permission_config import PERMISSION_CONFIG
from celery import shared_task


def assign_permission(user, role):

    role = "delivery_manager" if role == 2 else "seller" if role == 3 else "customer"

    role_permission = PERMISSION_CONFIG.get(role, {})

    for model, permissions in role_permission.items():

        content_type = ContentType.objects.get_for_model(
            model
        )  # returns the ContentType instance representing that model

        for perm_codename in permissions:

            permission = Permission.objects.get(
                content_type=content_type,
                codename=f"{perm_codename}_{model._meta.model_name}",
            )

            user.user_permissions.add(permission)


def generate_otp():
    return hotp(key=b"12345678901234567890", counter=random.randint(1, 9), digits=6)


@shared_task
def mailer(subject, body, to: List[str]):
    email = EmailMultiAlternatives(
        subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
    )

    email.send()
