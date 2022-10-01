from django.test import TestCase
from mock import Mock
from django.utils import timezone
from testApp.middleware.custom_middleware import LogsMiddleware

class StashMiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = LogsMiddleware()
        self.request = Mock()
        self.request.session = {}
        
    def test_process_request_without_stash(self, request):
        if not request.session.session_key:
            request.session.create()
            
        logs_data = dict()
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        logs_data["ip_address"] = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        logs_data["timestamp"] = timezone.now()
        
        self.assertEqual(logs_data["ip_address"], '127.0.0.1')
            
        response = self.get_response(request)
        return response
        