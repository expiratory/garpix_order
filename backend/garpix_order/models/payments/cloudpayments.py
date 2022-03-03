from ..invoice import BaseInvoice
from django.db import models
import uuid


def generate_uuid():
    return uuid.uuid4().hex


class CloudPaymentInvoice(BaseInvoice):
    PAYMENT_STATUS_AWAITING_AUTHENTICATION = 'AwaitingAuthentication'
    PAYMENT_STATUS_AUTHORIZED = 'Authorized'
    PAYMENT_STATUS_COMPLETED = 'Completed'
    PAYMENT_STATUS_CANCELLED = 'Cancelled'
    PAYMENT_STATUS_DECLINED = 'Declined'

    MAP_STATUS = {
        PAYMENT_STATUS_AWAITING_AUTHENTICATION: BaseInvoice.InvoiceStatus.WAITING_FOR_CAPTURE,
        PAYMENT_STATUS_AUTHORIZED: BaseInvoice.InvoiceStatus.PENDING,
        PAYMENT_STATUS_COMPLETED: BaseInvoice.InvoiceStatus.SUCCEEDED,
        PAYMENT_STATUS_CANCELLED: BaseInvoice.InvoiceStatus.CANCELED,
        PAYMENT_STATUS_DECLINED: BaseInvoice.InvoiceStatus.FAILED,
    }
    payment_uuid = models.CharField(max_length=64, verbose_name='UUID', default=generate_uuid)
    order_number = models.CharField(max_length=200, verbose_name='Номер заказа')
    transaction_id = models.CharField(max_length=200, default='', blank=True, verbose_name='Номер транзакции')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма платежа')
    is_test = models.BooleanField(default=False, verbose_name='Тестовый платеж')

    class Meta:
        verbose_name = 'Платеж Cloudpayment'
        verbose_name_plural = 'Платежи Cloudpayment'
