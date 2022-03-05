from ..payment import BasePayment
from django.db import models
import uuid


def generate_uuid():
    return uuid.uuid4().hex


class CloudPayment(BasePayment):
    PAYMENT_STATUS_AWAITING_AUTHENTICATION = 'AwaitingAuthentication'
    PAYMENT_STATUS_AUTHORIZED = 'Authorized'
    PAYMENT_STATUS_COMPLETED = 'Completed'
    PAYMENT_STATUS_CANCELLED = 'Cancelled'
    PAYMENT_STATUS_DECLINED = 'Declined'

    MAP_STATUS = {
        PAYMENT_STATUS_AWAITING_AUTHENTICATION: BasePayment.PaymentStatus.WAITING_FOR_CAPTURE,
        PAYMENT_STATUS_AUTHORIZED: BasePayment.PaymentStatus.PENDING,
        PAYMENT_STATUS_COMPLETED: BasePayment.PaymentStatus.SUCCEEDED,
        PAYMENT_STATUS_CANCELLED: BasePayment.PaymentStatus.CANCELED,
        PAYMENT_STATUS_DECLINED: BasePayment.PaymentStatus.FAILED,
    }
    payment_uuid = models.CharField(max_length=64, verbose_name='UUID', default=generate_uuid)
    order_number = models.CharField(max_length=200, verbose_name='Номер заказа')
    transaction_id = models.CharField(max_length=200, default='', blank=True, verbose_name='Номер транзакции')
    is_test = models.BooleanField(default=False, verbose_name='Тестовый платеж')

    class Meta:
        verbose_name = 'Платеж Cloudpayment'
        verbose_name_plural = 'Платежи Cloudpayment'
