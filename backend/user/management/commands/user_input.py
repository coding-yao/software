from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from user.models import User, Fisher  # 替换为您的应用

class Command(BaseCommand):
    help = '插入初始用户数据'

    def handle(self, *args, **kwargs):
        # 创建管理员
        admin = User.objects.create(
            id=1,
            account='1',
            password=make_password('1'),
            role='admin',
            is_active=True,
            is_staff=True
        )
        
        # 创建普通用户
        viewer = User.objects.create(
            id=2,
            account='22',
            password=make_password('22'),
            role='viewer',
            is_active=True,
            is_staff=False
        )
        
        # 创建渔民
        Fisher.objects.create(
            id=1,
            user=viewer
        )
        
        self.stdout.write(self.style.SUCCESS('数据插入成功!'))