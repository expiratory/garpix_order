import pytest
from decimal import Decimal
from django.urls import reverse
from garpix_order.models.payments.cloudpayments import CloudPayment
from garpix_order.models import Config
from garpix_order.utils import hmac_sha256
from garpix_order.models import BaseOrder
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def config(db):
    c = Config.get_solo()
    c.cloudpayments_public_id = 'test_public_id'
    c.cloudpayments_password_api = 'test_api_password'
    c.save()
    return c

@pytest.fixture
def base_order(db):
    user = User.objects.create_user('test', 'test@test.ru', 'test_password')
    return BaseOrder.objects.create(
        user=user,
        total_amount=1000,
        number="order_123"
    )

@pytest.fixture
def payment(db, base_order):
    return CloudPayment.objects.create(
        order=base_order,
        amount=Decimal('100.00'),
        order_number='12345'
    )

@pytest.mark.django_db
class TestCloudPayments:
    @pytest.mark.parametrize("payment_uuid_exist", [True, False])
    def test_payment_data_view(self, client, config, payment, payment_uuid_exist):
        url = '/cloudpayments/payment_data/'
        payment_uuid = payment.payment_uuid if payment_uuid_exist else 'nonexistent'
        response = client.get(url, {'payment_uuid': payment_uuid})
        data = response.json()
        if payment_uuid_exist:
            assert response.status_code == 200
            assert data['publicId'] == config.cloudpayments_public_id
            assert data['amount'] == str(payment.amount)
            assert data['invoiceId'] == payment.order_number
        else:
            assert response.status_code == 200
            assert 'error' in data

    def test_default_view_correct_hmac(self, client, config, payment):
        url = '/cloudpayments/pay/'
        post_data = {
            'InvoiceId': payment.payment_uuid,
            'Amount': '100.00',
            'Status': 'Completed',
            'TestMode': '1',
            'TransactionId': 'tx_123'
        }
        hmac_string = '&'.join([f'{k}={v}' for k, v in post_data.items()])
        local_hmac = hmac_sha256(hmac_string, config.cloudpayments_password_api).decode('utf-8')

        response = client.post(url, post_data, HTTP_X_CONTENT_HMAC=local_hmac)
        data = response.json()
        assert response.status_code == 200
        assert data['code'] == 0
        payment.refresh_from_db()
        assert payment.status == CloudPayment.PAYMENT_STATUS_COMPLETED
        assert payment.transaction_id == 'tx_123'
        assert payment.is_test is True

    def test_default_view_wrong_hmac(self, client, config, payment):
        url = '/cloudpayments/pay/'
        post_data = {
            'InvoiceId': payment.payment_uuid,
            'Amount': '100.00',
            'Status': 'Completed',
        }
        response = client.post(url, post_data, HTTP_X_CONTENT_HMAC='wrong_hmac')
        data = response.json()
        assert response.status_code == 200
        assert data['code'] == 13

    def test_default_view_wrong_amount(self, client, config, payment):
        url = '/cloudpayments/pay/'
        post_data = {
            'InvoiceId': payment.payment_uuid,
            'Amount': '200.00',
            'Status': 'Completed',
        }
        hmac_string = '&'.join([f'{k}={v}' for k, v in post_data.items()])
        local_hmac = hmac_sha256(hmac_string, config.cloudpayments_password_api).decode('utf-8')
        response = client.post(url, post_data, HTTP_X_CONTENT_HMAC=local_hmac)
        data = response.json()
        assert response.status_code == 200
        assert data['code'] == 12

    def test_fail_view(self, client, config, payment):
        url = '/cloudpayments/fail/'
        post_data = {
            'InvoiceId': payment.payment_uuid,
            'Amount': '100.00',
            'Status': 'Completed',
        }
        response = client.post(url, post_data)
        assert response.status_code == 200

    def test_pay_view_with_callback(self, client, config, payment):
        url = '/cloudpayments/pay/'
        post_data = {
            'InvoiceId': payment.payment_uuid,
            'Amount': '100.00',
            'Status': 'Completed',
        }
        hmac_string = '&'.join([f'{k}={v}' for k, v in post_data.items()])
        local_hmac = hmac_sha256(hmac_string, config.cloudpayments_password_api).decode('utf-8')

        response = client.post(url, post_data, HTTP_X_CONTENT_HMAC=local_hmac)
        data = response.json()
        assert response.status_code == 200
        assert data['code'] == 0
        payment.refresh_from_db()
        assert payment.status == CloudPayment.PAYMENT_STATUS_COMPLETED
