from django.db import models
from django.utils import timezone

class DeviceData(models.Model):
    """物联网设备数据模型"""
    device_id = models.SmallIntegerField(primary_key=True, verbose_name="设备ID")
    device_number = models.SmallIntegerField(unique=True, verbose_name="设备编号")
    device_data = models.CharField(max_length=256, verbose_name="设备采集数据")
    device_status = models.CharField(max_length=32, verbose_name="设备状态",
                                   choices=[('online','在线'),('offline','离线'),('fault','故障')])

    class Meta:
        verbose_name = "物联网设备"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"设备{self.device_number}(ID:{self.device_id})"

class SystemData(models.Model):
    """系统运行数据模型"""
    data_id = models.SmallIntegerField(primary_key=True, verbose_name="数据ID")
    memory_used = models.BigIntegerField(verbose_name="已用内存(Bytes)")
    memory_all = models.BigIntegerField(verbose_name="总内存(Bytes)")
    system_status = models.CharField(max_length=32, verbose_name="系统状态",
                                   choices=[('normal','正常'),('warning','警告'),('error','错误')])

    class Meta:
        verbose_name = "系统运行数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"系统快照#{self.data_id}"