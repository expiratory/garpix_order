import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status
from garpix_order.models import RobokassaPayment

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def robokassa_payment():
    return RobokassaPayment.objects.create(
        amount=100.00,
        description="Test Payment"
    )

@pytest.mark.django_db
class TestRobokassaView:
    def test_create_payment(self, api_client):
        url = reverse('garpix_order:robokassa-list')
        data = {
            "amount": 100.00,
            "description": "Test Payment"
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'payment_link' in response.data

    def test_list_payments(self, api_client, robokassa_payment):
        url = reverse('garpix_order:robokassa-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['amount'] == str(robokassa_payment.amount)

    def test_pay_success(self, api_client, robokassa_payment, mocker):
        url = reverse('garpix_order:robokassa-pay', args=[robokassa_payment.id])
        data = {
            "payment_data": "mocked_payment_data"
        }

        mocker.patch.object(RobokassaPayment, 'pay', return_value=(True, None))
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['result'] == 'success'

    def test_pay_failure(self, api_client, robokassa_payment, mocker):
        url = reverse('garpix_order:robokassa-pay', args=[robokassa_payment.id])
        data = {
            "payment_data": "mocked_payment_data"
        }

        mocker.patch.object(RobokassaPayment, 'pay', return_value=(False, "Error processing payment"))
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['result'] == ["Error processing payment"]
