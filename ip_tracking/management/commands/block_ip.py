from ip_tracking.models import BlockedIP
from django.core.management.base import BaseCommand


"""
Add ips to BlockedIP
"""
class Command(BaseCommand):
    help = 'Add ips to BlockedIP model'

    def add_arguments(self, parser):
        parser.add_argument('ip', nargs='+', type=str)

    def handle(self, *args, **options):
        ip_list = options.get('ip', [])
        if not ip_list:
            print("No ips provided")
            return
        for ip in ip_list:
            try:
                BlockedIP.objects.create(ip_address=ip)
                print(f"Ip {ip} added to BlockedIP")
            except Exception as e:
                print(f"Error creating ip: {e}")