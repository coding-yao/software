from django.db import models
from django.utils import timezone

class WaterData(models.Model):
    """水质监测数据模型"""
    location = models.CharField(max_length=30, db_index=True, verbose_name="省份")
    province = models.CharField(max_length=30, db_index=True, verbose_name="流域") 
    domain = models.CharField(max_length=50, db_index=True, verbose_name="断面名称")
    time = models.CharField(max_length=30, db_index=True, verbose_name="监测时间")
    water_type = models.SmallIntegerField(verbose_name="水质类别")
    temperature = models.FloatField(verbose_name="水温(℃)")
    ph = models.FloatField(verbose_name="pH")
    oxygen = models.FloatField(verbose_name="溶解氧(mg/L)")
    conductivity = models.FloatField(verbose_name="电导率(μS/cm)")
    turbidity = models.FloatField(verbose_name="浊度(NTU)")
    kmno4 = models.FloatField(verbose_name="高锰酸盐指数(mg/L)")
    nh4 = models.FloatField(verbose_name="氨氮(mg/L)")
    all_p = models.FloatField(verbose_name="总磷(mg/L)")
    all_n = models.FloatField(verbose_name="总氮(mg/L)")
    iaa_alpha = models.FloatField(verbose_name="叶绿素α(Bq/L)")
    cells = models.FloatField(verbose_name="藻密度(个/L)")
    status = models.CharField(max_length=32, verbose_name="站点情况")

    class Meta:
        unique_together = ('location', 'province', 'domain', 'time')  # 联合唯一键
        verbose_name = "水质监测数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.location}-{self.time}水质数据"

class WeatherData(models.Model):
    """气象监测数据模型"""
    location = models.CharField(max_length=30, db_index=True, verbose_name="省份")
    province = models.CharField(max_length=30, db_index=True, verbose_name="流域")
    domain = models.CharField(max_length=50, db_index=True, verbose_name="断面名称") 
    time = models.CharField(max_length=30, db_index=True, verbose_name="监测时间")
    temperature_h = models.FloatField(verbose_name="最高温度(℃)")
    temperature_l = models.FloatField(verbose_name="最低温度(℃)")
    wind_level = models.FloatField(verbose_name="风力等级")
    aqi = models.CharField(max_length=32, verbose_name="空气质量指数")
    wind_forward = models.CharField(max_length=32, verbose_name="风向")
    light = models.SmallIntegerField(verbose_name="光照强度(lx)")
    humidity = models.SmallIntegerField(verbose_name="相对湿度(%)")

    class Meta:
        unique_together = ('location', 'province', 'domain', 'time')
        verbose_name = "气象监测数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.location}-{self.time}气象数据"