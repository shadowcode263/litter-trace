"""User models."""
from typing import Iterable
import uuid
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# pylint: disable=no-name-in-module
from users.managers import CustomUserManager


class UserRoles(models.TextChoices):
    """User roles."""
    DEFAULT = 'DEFAULT', _('DEFAULT')
    ADMIN = 'ADMIN', _('ADMINISTRATOR')

class User(AbstractUser):
    """User model."""""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, blank=False, unique=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    title = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=100, blank=False, unique=True)
    email = models.EmailField()
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=100, choices=UserRoles.choices)
    password_updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile_number']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        """Meta class."""""
        ordering = ["first_name"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password
        self.password_updated_at = timezone.now()
        self.save()

    
