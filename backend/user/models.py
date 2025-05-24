from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=16, default='user')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'account'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.account



class Fisher(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fisher')

    def __str__(self):
        return f'Fisher {self.id} (user {self.user.account})'