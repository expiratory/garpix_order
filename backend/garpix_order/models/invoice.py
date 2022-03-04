from django.db import models
from polymorphic.models import PolymorphicModel
from .order import BaseOrder
from django_fsm import RETURN_VALUE, FSMField, TransitionNotAllowed, transition
from django.utils.translation import gettext_lazy as _


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
    client_data = models.JSONField(verbose_name='Client payment process data', blank=True, null=True)
    provider_data = models.JSONField(verbose_name='Provider payment process data', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def pay_full(self):
        self.order.pay_full()
        self.order.save()  # сохраняем для верности

    def pay_partially(self, item):
        self.order.pay_partially(item)
        self.order.save()

    @transition(field=status, source=[InvoiceStatus.CREATED, ], target=InvoiceStatus.PENDING)
    def pending(self):
        pass

    @transition(field=status, source=[InvoiceStatus.PENDING, ], target=InvoiceStatus.WAITING_FOR_CAPTURE)
    def waiting_for_capture(self):
        pass

    def can_succeeded(self):
        """Основные проверки при оплате"""
        order = self.order
        total_amount = order.total_amount
        payed_amount = order.payed_amount
        amount = self.amount
        if amount <= 0:
            return False
        if payed_amount + amount > total_amount:
            return False
        if amount != total_amount:
            return False
        return True

    @transition(
        field=status,
        source=[InvoiceStatus.CREATED, InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
        target=InvoiceStatus.SUCCEEDED,
        conditions=[can_succeeded]
    )
    def succeeded(self):
        self.pay_full()

    def can_succeeded_partially(self):
        """Основные проверки при оплате"""
        order = self.order
        total_amount = order.total_amount
        payed_amount = order.payed_amount
        amount = self.amount
        if amount <= 0:
            return False
        if payed_amount + amount > total_amount:
            return False
        return True

    @transition(
        field=status,
        source=[InvoiceStatus.CREATED, InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
        target=RETURN_VALUE(InvoiceStatus.SUCCEEDED, InvoiceStatus.FAILED),
        conditions=[can_succeeded_partially]
    )
    def succeeded_partially(self, item=None):
        """Если не переделаи оплачиваемый элемент, то переводим в failed"""
        try:
            self.pay_partially(item)
            return self.InvoiceStatus.SUCCEEDED
        except:
            return self.InvoiceStatus.FAILED

    @transition(field=status,
                source=[InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
                target=InvoiceStatus.CANCELED, on_error=InvoiceStatus.FAILED)
    def canceled(self):
        pass

    def can_refund(self):
        order = self.order
        amount = self.amount
        if order.payed_amount != amount:
            return False
        if order.status != order.OrderStatus.PAYED_FULL:
            return False
        if order.total_amount != order.payed_amount:
            return False
        return True

    @transition(
        field=status,
        source=[InvoiceStatus.CREATED, InvoiceStatus.PENDING, InvoiceStatus.WAITING_FOR_CAPTURE],
        target=InvoiceStatus.REFUNDED,
        on_error=InvoiceStatus.FAILED,
        conditions=[can_refund]
    )
    def refunded(self):
        self.order.refunded_full()
        self.order.save()

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
