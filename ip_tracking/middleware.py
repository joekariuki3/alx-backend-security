from datetime import datetime


class LogRequestDetailsMiddleware:
    """
    Middleware to log the ip address, timestamp,
    and path of every incoming request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        request.META['REQUEST_TIME'] = datetime.now()
        print(f"Request from {request.META['REMOTE_ADDR']} at {request.META['REQUEST_TIME']}. Path: {request.path}")
        response = self.get_response(request)
        # Code to be executed for each request/response after

        return response
