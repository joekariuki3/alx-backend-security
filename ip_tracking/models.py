from django.db import models


class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField()

class SuspiciousIP(models.Model):
    ip_address = models.GenericIPAddressField()
    reason = models.TextField()

    def __str__(self):
        return f"{self.ip_address} - {self.reason[:50]}"