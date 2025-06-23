from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=16, default='viewer')
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
    
    # 预警阈值配置
    weight_deviation_multiplier = models.FloatField(default=3.0, verbose_name="重量标准差倍数阈值")
    length_min = models.FloatField(default=5.0, verbose_name="最小长度阈值(cm)")
    length_max = models.FloatField(default=150.0, verbose_name="最大长度阈值(cm)")
    aspect_ratio_min = models.FloatField(default=1.5, verbose_name="最小长宽比阈值")
    aspect_ratio_max = models.FloatField(default=5.0, verbose_name="最大长宽比阈值")
    height_width_ratio_min = models.FloatField(default=0.2, verbose_name="最小高宽比阈值")
    height_width_ratio_max = models.FloatField(default=0.8, verbose_name="最大高宽比阈值")
    daily_mortality_rate_threshold = models.FloatField(default=0.02, verbose_name="日死亡率阈值(%)")
    
    def __str__(self):
        return f'Fisher {self.id} (user {self.user.account})'
