from celery import shared_task
from ip_tracking.models import RequestLog, SuspiciousIP
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta


SENSITIVE_PATHS = ['/admin/', '/login']

@shared_task
def flag_suspicious_ip():
    now = timezone.now()
    window_start = now - timedelta(hours=1)

    past_hour_logs = RequestLog.objects.filter(timestamp__gte=window_start)
    print(f"Past hour logs: {past_hour_logs.count()}")

    # IPs with more than 100 requests in the past hour
    heavy_traffic_ips = (
        past_hour_logs.values('ip_address')
        .annotate(total_requests=Count('ip_address'))
        .filter(total_requests__gt=100)
    )
    print(f"Heavy traffic IPs: {heavy_traffic_ips.count()}")

    for entry in heavy_traffic_ips:
        ip = entry.get('ip_address')
        total_requests = entry.get('total_requests')

        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason=f"Heavy traffic: {total_requests} requests in the past hour"
        )

    # IPs that accessed sensitive paths in the past hour
    sensitive_hits = (
        past_hour_logs.filter(path__in=SENSITIVE_PATHS)
        .values('ip_address', 'path')
        .distinct()
    )
    print(f"Sensitive hits: {sensitive_hits.count()}")

    for hit in sensitive_hits:
        ip = hit.get('ip_address')
        path = hit.get('path')
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason=f"Accessing sensitive path: {path}"
        )