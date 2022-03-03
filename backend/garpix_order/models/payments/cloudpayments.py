from ..invoice import BaseInvoice
from django.db import models
import uuid


def generate_uuid():
    return uuid.uuid4().hex


class CloudPaymentInvoice(BaseInvoice):
    MAP_STATUS = {
        'AwaitingAuthentication': BaseInvoice.InvoiceStatus.WAITING_FOR_CAPTURE,
        'Authorized': BaseInvoice.InvoiceStatus.PENDING,
        'Completed': BaseInvoice.InvoiceStatus.SUCCEEDED,
        'Cancelled': BaseInvoice.InvoiceStatus.CANCELED,
        'Declined': BaseInvoice.InvoiceStatus.FAILED,
    }
    payment_uuid = models.CharField(max_length=64, verbose_name='UUID', default=generate_uuid)
    order_number = models.CharField(max_length=200, verbose_name='Номер заказа')
    transaction_id = models.CharField(max_length=200, default='', blank=True, verbose_name='Номер транзакции')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма платежа')
    is_test = models.BooleanField(default=False, verbose_name='Тестовый платеж')

    class Meta:
        verbose_name = 'Платеж Cloudpayment'
        verbose_name_plural = 'Платежи Cloudpayment'
