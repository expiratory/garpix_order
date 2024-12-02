import json
from django.conf import settings
from rest_framework.test import APITestCase
from app.tests import TestMixin
from garpix_order.models import Config
from garpix_order.models.order import BaseOrder
from garpix_order.models.payments.cloudpayments import CloudPayment

class PaymentDataViewTestCase(TestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls._create_user()

    def test_payment_data_view(self):
        config = Config.get_solo()
        order = BaseOrder.objects.create(user=self.user, total_amount=300, number='test')
        payment = CloudPayment.objects.create(
            title='test',
            order=order,
            amount=300,
            order_number=str(order.id),
            is_test=True,
        )

        expected_response_data = {
            'publicId': config.cloudpayments_public_id,
            'description': 'Оплата товара',
            'amount': f'{payment.amount}.00',
            'currency': 'RUB',
            'invoiceId': payment.order_number,
            'skin': "mini",
        }

        response = self.client.get(f'/cloudpayments/payment_data/?payment_uuid={payment.payment_uuid}')
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(content, expected_response_data)

    def test_payment_data_view_non_existing_cloudpayment_uuid(self):
        response = self.client.get('/cloudpayments/payment_data/?payment_uuid=non_existing_uuid')
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, {'error': 'Does not exist'})
