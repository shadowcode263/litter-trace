"""Custom user model managers."""
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifiers"""

    def create_superuser(self, username, password, **other_fields):
        """Create and save a SuperUser with the given email and password."""""
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.'
            )
        return self.create_user(username, password, **other_fields)

    def create_user(self, username, password, **other_fields):
        """Create and save a User with the given email and password."""
        if not username:
            raise ValueError(
                'You must provide username'
            )
        user = self.model(username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user
