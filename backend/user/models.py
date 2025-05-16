from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)  
    account = models.CharField(max_length=32, unique=True) 
    password = models.CharField(max_length=128)  
    role = models.CharField(max_length=16, default='user') 
    is_approved = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account


class Fisher(models.Model):
    fisher_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fisher')

    def __str__(self):
        return f'Fisher {self.fisher_id} (user {self.user.account})'
