import json

from django.db import models
from polymorphic.models import PolymorphicModel
from django_fsm import RETURN_VALUE, FSMField, transition
from django.utils.translation import gettext_lazy as _


class BasePayment(PolymorphicModel):
    """
    Базовая модель для хранения полученыых платежей по заказу.
    Можно наследоваться для создания своих способов оплаты.
    """

    class PaymentStatus:
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

    class PaymentType(models.TextChoices):
        """Тип платежа"""
        MANUAL = 'MANUAL', _('Ручной')
        AUTO = 'AUTO', _('Автоматический')

    title = models.CharField(max_length=255, verbose_name=_('Название'), default='')
    order = models.ForeignKey('garpix_order.BaseOrder', on_delete=models.CASCADE, verbose_name=_('Заказ'),
                              related_name='payments')
    amount = models.DecimalField(decimal_places=2, max_digits=12, verbose_name=_('Сумма'), default=0)
    status = FSMField(choices=PaymentStatus.CHOICES, default=PaymentStatus.CREATED)
    client_data = models.JSONField(verbose_name=_('Данные процесса оплаты клиента'), blank=True, null=True)
    provider_data = models.JSONField(verbose_name=_('Данные процесса оплаты провайдера'), blank=True, null=True)
    payment_type = models.CharField(max_length=6, choices=PaymentType.choices, default=PaymentType.MANUAL,
                                    verbose_name=_('Тип платежа'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата изменения'))

    @classmethod
    def make_refunded(cls, instance):
        payment = cls.objects.create(
            title=f'{instance.title}_refunded',
            order=instance.order,
            amount=instance.amount
        )
        return payment

    def pay_full(self):
        self.order.pay(payment=self)
        self.order.save()  # сохраняем для верности

    @transition(field=status, source=[PaymentStatus.CREATED, ], target=PaymentStatus.PENDING)
    def pending(self):
        pass

    @transition(field=status, source=[PaymentStatus.PENDING, ], target=PaymentStatus.WAITING_FOR_CAPTURE)
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
        return True

    @transition(
        field=status,
        source=[PaymentStatus.CREATED, PaymentStatus.PENDING, PaymentStatus.WAITING_FOR_CAPTURE],
        target=PaymentStatus.SUCCEEDED,
        conditions=[can_succeeded]
    )
    def succeeded(self):
        self.pay_full()

    @transition(field=status,
                source=[PaymentStatus.PENDING, PaymentStatus.WAITING_FOR_CAPTURE],
                target=PaymentStatus.CANCELED, on_error=PaymentStatus.FAILED)
    def canceled(self):
        pass

    def can_refund(self):
        order = self.order
        if order.status in (order.OrderStatus.PAYED_FULL, order.OrderStatus.PAYED_PARTIAL,):
            return True
        return False

    @transition(
        field=status,
        source=[PaymentStatus.CREATED, PaymentStatus.PENDING, PaymentStatus.WAITING_FOR_CAPTURE],
        target=PaymentStatus.REFUNDED,
        on_error=PaymentStatus.FAILED,
        conditions=[can_refund]
    )
    def refunded(self):
        self.order.refunded(payment=self)
        self.order.save()

    @transition(field=status, source=[PaymentStatus.CREATED, PaymentStatus.PENDING, PaymentStatus.WAITING_FOR_CAPTURE],
                target=PaymentStatus.FAILED)
    def failed(self):
        pass

    @transition(field=status, source=[PaymentStatus.PENDING, PaymentStatus.WAITING_FOR_CAPTURE],
                target=PaymentStatus.TIMEOUT)
    def timeout(self):
        pass

    @transition(field=status, source='*', target=PaymentStatus.CLOSED)
    def closed(self):
        pass

    def set_provider_data(self, data):
        self.provider_data = json.dumps(data)
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Базовый платеж')
        verbose_name_plural = _('Базовые платежи')
