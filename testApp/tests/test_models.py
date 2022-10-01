from django.test import TestCase
from ..models import LogsModel

class ModelsTestCase(TestCase):
    def test_logs_model(self):
        ip_address="192.168.1"
        self.assertEqual(ip_address, "192.168.1")