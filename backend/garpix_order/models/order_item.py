from decimal import Decimal
from django.db import models
from django_fsm import FSMField, transition
from polymorphic.models import PolymorphicModel


class BaseOrderItem(PolymorphicModel):
    class OrderItemStatus:
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


    status = FSMField(choices=OrderItemStatus.CHOICES, default=OrderItemStatus.CREATED)
    order = models.ForeignKey('garpix_order.BaseOrder', on_delete=models.CASCADE, verbose_name="Заказ")
    amount = models.DecimalField(verbose_name='Цена', default=0, max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def full_amount(self) -> Decimal:
        return self.amount * self.quantity

    @transition(
        field=status,
        source=OrderItemStatus.CREATED,
        target=OrderItemStatus.PAYED_FULL
    )
    def pay(self):
        pass

    @transition(
        field=status,
        source=(OrderItemStatus.PAYED_FULL, OrderItemStatus.PAYED_PARTIAL,),
        target=OrderItemStatus.REFUNDED
    )
    def refunded(self):
        pass

    class Meta:
        verbose_name = 'Продукт заказа'
        verbose_name_plural = 'Продукты заказа'

    def __str__(self):
        return f'Объект заказа - {self.order}'
