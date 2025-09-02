# IP Tracking: Security and Analytics

A Django-based project that demonstrates practical web application security and analytics techniques by tracking incoming requests, rate‑limiting logins, flagging suspicious activity, and supporting automated background processing with Celery.

This project can be used as a learning aid or as a starting point for adding request auditing and basic threat signals to a Django app.


## Key Features

- Request logging middleware
  - Logs client IP, timestamp, request path, and geo info (country/city via ipapi.co) on every request
  - Caches IP geolocation in Redis to reduce external API calls
  - Blocks requests from blacklisted IPs with HTTP 403
- Suspicious activity detection (Celery task)
  - Flags IPs generating heavy traffic (>100 requests in past hour)
  - Flags IPs that access sensitive paths ("/admin/", "/login")
  - Runs hourly via django-celery-beat schedule
- Authentication demo with rate limiting
  - Login view protected with django-ratelimit using dynamic rate: 5/min for anonymous, 10/min for authenticated
  - Basic auth flow with login, logout, and a protected profile page
- Admin/management utilities
  - Django admin enabled
  - Custom management command to block IPs (ip_tracking.management.commands.block_ip)
- Simple UI templates for home, login, logout, and profile


## Project Structure

- alx_backend_security/ — Django project settings and ASGI/WSGI
- ip_tracking/ — Application with middleware, models, Celery tasks, URLs, views, templates
- ip_tracking/migrations/ — Database migrations for RequestLog, BlockedIP, SuspiciousIP
- manage.py — Django management CLI entrypoint
- pyproject.toml, uv.lock — Python dependency management (uv/pip compatible)


## Requirements

- Python 3.10+ (recommended)
- Redis server (for cache and Celery broker)
- SQLite (default) or another DB supported by Django

Python dependencies (installed via `uv` or pip):
- Django
- requests
- django-ratelimit
- celery
- django-celery-results
- django-celery-beat
- redis (Python client)

See pyproject.toml for exact versions.


## Getting Started

1. Clone and enter the project directory
   - git clone https://github.com/joekariuki3/alx-backend-security.git
   - cd alx-backend-security

2. Create and activate a virtual environment or use uv and install dependencies
   - `uv init`
    - `uv sync`
    - create a virtual environment:
      - `python -m venv .venv`
      - `source .venv/bin/activate`  (Windows: `.venv\\Scripts\\activate`)
      - Install dependencies 
        - `pip install -r requirements.txt`

3. Configure environment
   - Ensure Redis is running locally on 127.0.0.1:6379
   - For production, set DEBUG=False, SECRET_KEY, and proper ALLOWED_HOSTS

4. Initialize the database
   - `python manage.py migrate`
   - `python manage.py createsuperuser`  (to access /admin/)

5. Run the development server
   - `python manage.py runserver`
   - Visit http://127.0.0.1:8000/


## Running Celery and Beat

This project uses Redis for the Celery broker and django-celery-results for result backend.

- Start a Redis server
  - macOS (brew): `brew services start redis`
  - Linux: `sudo systemctl start redis-server` (or `redis`)
  - Docker (alternative): `docker run -p 6379:6379 redis:latets`

- Start Celery worker (in a new terminal)
  - `source .venv/bin/activate`
  - `celery -A ip_tracking worker --loglevel=INFO`

- Start Celery beat scheduler (in another terminal)
  - `source .venv/bin/activate`
  - `celery -A ip_tracking beat --loglevel=INFO`

The hourly task ip_tracking.tasks.flag_suspicious_ip is defined in settings via CELERY_BEAT_SCHEDULE and will run every hour to flag heavy traffic or sensitive path access.


## Application URLs

Defined in ip_tracking/urls.py:
- / — Home page
- /login/ — Login form (rate‑limited)
- /logout/ — Logout page
- /profile/ — Authenticated profile page (login required)

If you enabled Django admin (INSTALLED_APPS includes django.contrib.admin), the project root urls.py may expose /admin/ as usual.


## Middleware Behavior

The ip_tracking.middleware.LogRequestDetailsMiddleware:
- Extracts ip_address from REMOTE_ADDR (or "Unknown") and a timestamp
- Calls ipapi.co to obtain country and city for the IP, caching results in Redis for 24h
- Writes a RequestLog record for every request
- Checks BlockedIP; if a client IP is present, returns HTTP 403 immediately

Note: In many deployments, client IP might be found in headers like X-Forwarded-For. You may want to adapt REMOTE_ADDR extraction behind proxies/load balancers.


## Data Model Overview

- RequestLog
  - ip_address: GenericIPAddressField
  - timestamp: DateTime
  - path: string
  - country, city: optional strings
- BlockedIP
  - ip_address: GenericIPAddressField (requests get 403)
- SuspiciousIP
  - ip_address: GenericIPAddressField
  - reason: Text explaining why it was flagged


## Detecting Suspicious Activity

The periodic task ip_tracking.tasks.flag_suspicious_ip:
- Scans RequestLog entries from the past hour
- Flags IPs with more than 100 requests in that window
- Flags IPs that accessed sensitive paths ("/admin/", "/login")
- Creates/keeps SuspiciousIP records with specific reasons

You can tune the heuristic by editing SENSITIVE_PATHS and the threshold in tasks.py.


## Rate Limiting

The login view uses django-ratelimit with a key of user_or_ip and a dynamic rate defined in views.get_rate:
- Anonymous: 5 requests/minute
- Authenticated: 10 requests/minute

When limits are exceeded, the decorator blocks the request.


## Management Command: Block IP

A custom command is included to add IPs to the BlockedIP list.

Example:
- python manage.py block_ip --ip 203.0.113.9

After blocking, subsequent requests from that IP will receive HTTP 403 via the middleware.


## Running Tests

- python manage.py test

Tests reside under ip_tracking/tests.py. Add your own tests to cover additional behaviors and edge cases.


## Configuration Notes

Important settings (alx_backend_security/settings.py):
- INSTALLED_APPS includes ip_tracking, django_celery_results, django_celery_beat
- MIDDLEWARE includes ip_tracking.middleware.LogRequestDetailsMiddleware
- CACHES configured to Redis at redis://127.0.0.1:6379
- CELERY_BROKER_URL uses Redis; CELERY_RESULT_BACKEND is django-db; beat uses DatabaseScheduler

For production:
- Set SECRET_KEY via environment
- Set DEBUG=False and proper ALLOWED_HOSTS
- Consider a robust IP extraction method (e.g., X-Forwarded-For with trusted proxies)
- Add timeouts/retries for geolocation requests and consider circuit-breaking


## Troubleshooting

- Redis connection errors
  - Ensure Redis is running and accessible at 127.0.0.1:6379 or change settings accordingly
- Celery worker not picking tasks
  - Confirm worker and beat are started with the same app path (-A ip_tracking)
  - Check that django_celery_beat tables exist (run migrations)
- Geolocation shows "Unknown"
  - ipapi.co may rate limit or not resolve private IPs (e.g., 127.0.0.1). This is expected in development
- 403 responses unexpectedly
  - Check BlockedIP entries in the database/admin


## License
MIT License

## Acknowledgements

- Django web framework
- django-ratelimit for request throttling
- Celery, django-celery-results, django-celery-beat for task scheduling
- ipapi.co for geolocation data (public API)
