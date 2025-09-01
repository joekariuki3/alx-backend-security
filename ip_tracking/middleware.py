from datetime import datetime
from .models import BlockedIP, RequestLog
from django.http import HttpResponseForbidden
import requests
from django.core.cache import cache

class LogRequestDetailsMiddleware:
    """
    Middleware to log the ip address, timestamp,
    and path of every incoming request.
    """
    CACHE_TIMEOUT = 60*60*24
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        date_time = request.META.get('REQUEST_TIME', datetime.now())
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
        path = request.path
        country, city = self.get_country_city(ip_address)
        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=date_time,
            path=path,
            country=country,
            city=city,
        )
        print(f"Request from {ip_address} at {date_time}. Path: {path}")

        blacklisted_ip = BlockedIP.objects.filter(ip_address=ip_address).exists()
        if blacklisted_ip:
            return HttpResponseForbidden("Forbidden", status=403)

        response = self.get_response(request)
        # Code to be executed for each request/response after

        return response

    def get_geolocation_from_api(self, ip_address):
        url = f"https://ipapi.co/{ip_address}/json/"
        try:
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(f"Error getting geolocation: {e}")
            return

    def get_country_city(self, ip_address):
        if cache.get(ip_address):
            country, city = cache.get(ip_address)
            print(f"Using cached country and city for {ip_address}")
        else:
            geolocation = self.get_geolocation_from_api(ip_address)
            country = geolocation.get('country_name', 'Unknown')
            city = geolocation.get('city', 'Unknown')
            cache.set(ip_address, (country, city), timeout=self.CACHE_TIMEOUT)
        return country, city