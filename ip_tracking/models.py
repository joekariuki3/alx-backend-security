from django.db import models


class RequestLog(models.Model):
    ip_address = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
