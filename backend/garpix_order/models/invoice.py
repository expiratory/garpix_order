from django.db import models
from polymorphic.models import PolymorphicModel
from .order import BaseOrder
from django_fsm import FSMField, transition
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class BaseInvoice(PolymorphicModel):
    class InvoiceStatus:
        CREATED = 'created'
        PENDING = 'pending'
        WAITING_FOR_CAPTURE = 'waiting_for_capture'
        SUCCEEDED = 'succeeded'
        CANCELED = 'cancel'
        FAILED = 'failed'
        REFUNDED = 'refunded'
        TIMEOUT = 'timeout'
        CLOSED = 'closed'

        CHOICES = (
            (CREATED, 'CREATED'),
            (PENDING, 'PENDING'),
            (WAITING_FOR_CAPTURE, 'WAITING FOR CAPTURE'),
            (SUCCEEDED, 'SUCCEEDED'),
            (CANCELED, 'CANCELED'),
            (FAILED, 'FAILED'),
            (REFUNDED, 'REFUNDED'),
            (TIMEOUT, 'TIMEOUT'),
            (CLOSED, 'CLOSED')
        )

    title = models.CharField(max_length=255, verbose_name='Название', default='')
    order = models.ForeignKey(BaseOrder, on_delete=models.CASCADE, verbose_name='Заказ', related_name='Заказ')
    amount = models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Сумма', default=0)
    status = FSMField(choices=InvoiceStatus.CHOICES, default=InvoiceStatus.CREATED)
    payment_type = models.CharField(default=settings.CHOICES_PAYMENT_TYPES[0][0],
                                    max_length=255,
                                    choices=settings.CHOICES_PAYMENT_TYPES, verbose_name='Тип оплаты')
    client_data = models.JSONField(verbose_name='Client payment process data', blank=True, null=True)
    provider_data = models.JSONField(verbose_name='Provider payment process data', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def clean(self, *args, **kwargs):
        order = self.order
        total_amount = order.total_amount
        payed_amount = order.payed_amount
        amount = self.amount
        if amount <= 0:
            raise ValidationError(_('Сумма должна быть больше 0'))
        if payed_amount + amount > total_amount:
            raise ValidationError(_('Сумма больше стоимости заказа'))

    def pay_full(self):
        self.order.pay_full()

    def cancel(self):
        self.order.cancel()

    @transition(field=status, source=[InvoiceStatus.CREATED, ], target=InvoiceStatus.PENDING)
    def pending(self):
        pass

    @transition(field=status, source=[InvoiceStatus.PENDING, ], target=InvoiceStatus.WAITING_FOR_CAPTURE)
    def waiting_for_capture(self):
        pass

    @transition(field=status, source=[InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
                target=InvoiceStatus.SUCCEEDED)
    def succeeded(self):
        self.pay_full()

    @transition(field=status,
                source=[InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE, InvoiceStatus.SUCCEEDED],
                target=InvoiceStatus.CANCELED, on_error=InvoiceStatus.FAILED)
    def canceled(self):
        self.cancel()

    @transition(field=status,
                source=[InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE, InvoiceStatus.SUCCEEDED],
                target=InvoiceStatus.REFUNDED, on_error=InvoiceStatus.FAILED)
    def refunded(self):
        pass

    @transition(field=status, source=[InvoiceStatus.CREATED, InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
                target=InvoiceStatus.FAILED)
    def failed(self):
        pass

    @transition(field=status, source=[InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
                target=InvoiceStatus.TIMEOUT)
    def timeout(self):
        pass

    @transition(field=status, source='*', target=InvoiceStatus.CLOSED)
    def closed(self):
        pass

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
