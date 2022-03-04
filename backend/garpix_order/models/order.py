from django.db import models, transaction
from django.db.models import F, Sum, DecimalField
from django_fsm import FSMField, transition
from polymorphic.models import PolymorphicModel
from django.conf import settings
from .order_item import BaseOrderItem


OrderItemStatus = BaseOrderItem.OrderItemStatus


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


    status = FSMField(choices=OrderStatus.CHOICES, default=OrderStatus.CREATED)
    number = models.CharField(max_length=255, verbose_name='Номер заказа')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Пользователь")
    total_amount = models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Полная стоимость')
    payed_amount = models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Оплачено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def make_instance(self):
        pass

    def items_all(self):
        return self.baseorderitem_set.all()

    def active_items(self):
        return self.items_all().exclude(status__in=(OrderItemStatus.CANCELED, OrderItemStatus.REFUNDED,))

    def items_amount(self):
        amount = self.active_items().aggregate(
            total=Sum(F('amount') * F('quantity'), output_field=DecimalField()))
        total = amount.get('total', 0)
        if total is None:
            return 0
        return amount.get('total', 0)

    def paid_items(self):
        return self.items_all().filter(status=BaseOrderItem.OrderItemStatus.PAYED_FULL)

    def paid_items_amount(self):
        amount = self.paid_items().aggregate(
            total=Sum(F('amount') * F('quantity'), output_field=DecimalField()))
        total = amount.get('total', 0)
        if total is None:
            return 0
        return total

    @transaction.atomic
    @transition(field=status, source=(OrderStatus.CREATED,), target=OrderStatus.PAYED_FULL)
    def pay_full(self):
        for item in self.active_items():
            item.pay()
            item.save()
        self.payed_amount = self.total_amount
        self.save()

    @transaction.atomic
    @transition(field=status, source=(OrderStatus.CREATED, OrderStatus.PAYED_PARTIAL), target=OrderStatus.PAYED_PARTIAL)
    def pay_partially(self, item):
        item.pay()
        item.save()
        self.payed_amount = self.paid_items_amount()

    @transaction.atomic
    @transition(field=status, source=(OrderStatus.PAYED_FULL, OrderStatus.PAYED_PARTIAL), target=OrderStatus.REFUNDED)
    def refunded_full(self):
        for item in self.active_items():
            item.refunded()
            item.save()
        self.payed_amount = 0
        self.save()
    
    def cancel(self):
        pass

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Базовый ордер'
        verbose_name_plural = 'Базовые ордера'
        ordering = ('-created_at',)
