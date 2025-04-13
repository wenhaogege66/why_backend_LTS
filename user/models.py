from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    avatar_url = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.nickname
