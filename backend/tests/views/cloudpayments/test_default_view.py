import json
from unittest.mock import patch
from urllib import parse
from django.conf import settings
from django.utils import timezone
from app.tests import TestMixin
from garpix_order.models.order import BaseOrder
from garpix_order.models.payment import BasePayment
from garpix_order.models.payments.robokassa import RobokassaPayment
from garpix_order.models.payments.recurring import Recurring
from garpix_order.services.robokassa import robokassa_service

class DefaultViewTestCase(TestMixin):
    @classmethod
    def setUpTestData(cls):
        cls._create_user()
