from datetime import datetime
from .models import BlockedIP
from django.http import HttpResponseForbidden, HttpResponse

class LogRequestDetailsMiddleware:
    """
    Middleware to log the ip address, timestamp,
    and path of every incoming request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        date_time = request.META.get('REQUEST_TIME', datetime.now())
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
        path = request.path
        print(f"Request from {ip_address} at {date_time}. Path: {path}")

        blacklisted_ip = BlockedIP.objects.filter(ip_address=ip_address).exists()
        if blacklisted_ip:
            return HttpResponseForbidden("Forbidden", status=403)

        response = self.get_response(request)
        # Code to be executed for each request/response after

        return response
