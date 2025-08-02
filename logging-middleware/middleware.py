from datetime import datetime

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Log request details
        request_method = environ.get('REQUEST_METHOD')
        path_info = environ.get('PATH_INFO')
        query_string = environ.get('QUERY_STRING')
        
        print(f"[{datetime.utcnow().isoformat()}] {request_method} {path_info}?{query_string}")
        
        # Call the actual app
        return self.app(environ, start_response)