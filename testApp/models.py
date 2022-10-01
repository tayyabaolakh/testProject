from django.db import models

# Create your models here.


class LogsModel(models.Model):
    ip_address = models.CharField(max_length=45, null=False, blank=True)
    timestamp = models.DateTimeField(null=False, blank=True)
        
    class Meta:
        verbose_name = 'logsModel'
        verbose_name_plural = 'logsModels'