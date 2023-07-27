import re

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F, Sum, DecimalField
from django_fsm import RETURN_VALUE, FSMField, transition
from polymorphic.models import PolymorphicModel
from garpix_order.models.payment import BasePayment
from garpix_order.models.payments.recurring import Recurring


class BaseOrder(PolymorphicModel):
    class OrderStatus:
        CREATED = 'created'
        PAYED_FULL = 'payed_full'
        PAYED_PARTIAL = 'payed_partial'
        REFUNDED = 'refunded'
        CANCELED = 'cancel'

        CHOICES = (
            (CREATED, 'CREATED'),
            (PAYED_FULL, 'PAYED_FULL'),
            (PAYED_PARTIAL, 'PAYED_PARTIAL'),
            (CANCELED, 'CANCELED'),
            (REFUNDED, 'REFUNDED'),
        )

    decimalfield_kwargs = {
        'max_digits': 12,
        'decimal_places': 2,
    }

    status = FSMField(choices=OrderStatus.CHOICES, default=OrderStatus.CREATED)
    number = models.CharField(max_length=255, verbose_name='Номер заказа')
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, verbose_name="Пользователь")
    total_amount = models.DecimalField(default=0, **decimalfield_kwargs, verbose_name='Полная стоимость')
    payed_amount = models.DecimalField(default=0, **decimalfield_kwargs, verbose_name='Оплачено')
    recurring = models.ForeignKey(Recurring, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Рекуррент')
    next_payment_date = models.DateTimeField(verbose_name='Дата слелующего платежа', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def make_full_payment(self, **kwargs):
        return BasePayment.objects.create(order=self, amount=self.total_amount, **kwargs)

    def items_all(self):
        return self.baseorderitem_set.all()

    def items_amount(self):
        amount = self.items_all().aggregate(
            total=Sum(F('amount') * F('quantity'), output_field=DecimalField()))
        total = amount.get('total', 0)
        if total is None:
            return 0
        return amount.get('total', 0)

    def payment_amount(self):
        payments = self.payments.all().filter(status=BasePayment.PaymentStatus.SUCCEEDED)
        result = payments.aggregate(
            total=Sum('amount')
        )
        total = result.get('total')
        if total is None:
            return 0
        return result.get('total')

    @transaction.atomic
    @transition(field=status, source=(OrderStatus.CREATED, OrderStatus.PAYED_PARTIAL,), target=RETURN_VALUE(OrderStatus.PAYED_FULL, OrderStatus.PAYED_PARTIAL))
    def pay(self, payment):
        self.payed_amount = self.payment_amount() + payment.amount
        if self.payed_amount == self.total_amount:
            return self.OrderStatus.PAYED_FULL
        return self.OrderStatus.PAYED_PARTIAL

    @transaction.atomic
    @transition(
        field=status,
        source=(OrderStatus.PAYED_FULL, OrderStatus.PAYED_PARTIAL),
        target=RETURN_VALUE(OrderStatus.REFUNDED, OrderStatus.PAYED_PARTIAL)
    )
    def refunded(self, payment):
        self.payed_amount = self.payed_amount - payment.amount
        if self.payed_amount == 0:
            return self.OrderStatus.REFUNDED
        return self.OrderStatus.PAYED_PARTIAL

    def cancel(self):
        pass

    @classmethod
    def split_order(cls, number, item):
        old_order = item.order
        if old_order.status == cls.OrderStatus.CREATED:
            order = cls.objects.create(number=number, user=old_order.user, total_amount=item.full_amount())
            item.order = order
            item.save()
            old_order.total_amount = old_order.items_amount()
            old_order.save()
            return order
        return None

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Базовый ордер'
        verbose_name_plural = 'Базовые ордера'
        ordering = ('-created_at',)
