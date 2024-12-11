import pytest
from unittest.mock import patch
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

import json
from garpix_order.services.sber import SberService
from garpix_order.models.order import BaseOrder
from garpix_order.models.payments.sber import SberPayment
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def base_order(db):
    user = User.objects.create_user('test', 'test@test.ru', 'test_password')
    return BaseOrder.objects.create(
        user=user,
        total_amount=1000,
        number="order_123"
    )


@pytest.fixture
def sber_payment(base_order, db):
    return SberPayment.objects.create(
        id=1,
        order=base_order,
        external_payment_id="external_123",
        payment_link="https://test.sberbank.ru/payment",
        status="created"
    )


@pytest.fixture
def sber_service():
    return SberService()


@pytest.mark.django_db
class TestSberService:
    @patch('garpix_order.services.sber.requests.get')
    def test_request_success(self, mock_get, sber_service):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = json.dumps({'orderId': '12345'}).encode('utf-8')

        response = sber_service._request(
            url='https://test.sberbank.ru/register',
            params={'token': 'test_token'}
        )

        assert response['orderId'] == '12345'
        mock_get.assert_called_once()

    @patch('garpix_order.services.sber.requests.get')
    def test_request_failure(self, mock_get, sber_service):
        mock_get.side_effect = Exception("Connection error")

        with pytest.raises(Exception, match="Connection error"):
            sber_service._request(
                url='https://test.sberbank.ru/register',
                params={'token': 'test_token'}
            )

    def test_compute_my_checksum(self, sber_service):
        checksum = sber_service._compute_my_checksum(
            secret_key=b'test_key',
            callback_data='test_data'
        )
        assert checksum == '46A5B27B7E6672271C998F4D79ED460FF03C88CACD31355FFC161539E1657824'

    @patch('garpix_order.services.sber.SberService._request')
    def test_create_payment_success(self, mock_request, base_order, sber_service):
        mock_request.return_value = {
            'orderId': 'external_123',
            'formUrl': 'https://test.sberbank.ru/payment'
        }

        payment = sber_service.create_payment(order=base_order, returnUrl='https://return.url')

        assert payment.external_payment_id == 'external_123'
        assert payment.payment_link == 'https://test.sberbank.ru/payment'
        assert payment.order == base_order

    @patch('garpix_order.services.sber.SberService._request')
    def test_create_payment_failure(self, mock_request, base_order, sber_service):
        mock_request.return_value = {'errorCode': 5}

        payment = sber_service.create_payment(order=base_order, returnUrl='https://return.url')

        assert payment.status == "failed"

    def test_callback_success(self, sber_service, sber_payment, mocker):
        mock_update_payment = mocker.patch.object(sber_service, 'update_payment')
        mock_compute_checksum = mocker.patch.object(
            sber_service,
            '_compute_my_checksum',
            return_value='valid_checksum'
        )

        data = {
            'mdOrder': 'external_123',
            'checksum': 'valid_checksum'
        }
        response = sber_service.callback(data)

        assert response.status_code == HTTP_200_OK
        mock_update_payment.assert_called_once_with(payment=sber_payment)

    def test_callback_invalid_checksum(self, sber_service, mocker):
        mock_compute_checksum = mocker.patch.object(
            sber_service,
            '_compute_my_checksum',
            return_value='invalid_checksum'
        )

        data = {
            'mdOrder': 'external_123',
            'checksum': 'valid_checksum'
        }
        response = sber_service.callback(data)

        assert response.status_code == HTTP_400_BAD_REQUEST
