from django.db import models
from user.models import User, Fisher

class Fish(models.Model):
    fish_id = models.AutoField(primary_key=True, verbose_name="鱼ID")
    fisher_id = models.ForeignKey(Fisher, on_delete=models.CASCADE, verbose_name="渔民ID")
    species = models.CharField(max_length=100, verbose_name="物种")
    weight = models.FloatField(verbose_name="重量（克）")
    length1 = models.FloatField(verbose_name="长度1（厘米）")
    length2 = models.FloatField(verbose_name="长度2（厘米）")
    length3 = models.FloatField(verbose_name="长度3（厘米）")
    height = models.FloatField(verbose_name="高度（厘米）")
    width = models.FloatField(verbose_name="宽度（厘米）")

    def __str__(self):
        return self.species