from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class Client(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        unique=True,
        db_index=True,
    )
    full_name = models.CharField(
        max_length=191,
        blank=True,
    )
    short_name = models.CharField(
        max_length=191,
        blank=True,
    )
    profile_picture = models.ImageField(
        blank=True, null=True, default='niceblog/blog-2_zq82wf.jpg'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.short_name

    def __str__(self):
        return f"{self.email}"
