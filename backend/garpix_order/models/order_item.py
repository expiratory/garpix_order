from decimal import Decimal
from django.db import models
from django_fsm import FSMField, transition
from polymorphic.models import PolymorphicModel


class BaseOrderItem(PolymorphicModel):
    order = models.ForeignKey('garpix_order.BaseOrder', on_delete=models.CASCADE, verbose_name="Заказ")
    amount = models.DecimalField(verbose_name='Цена', default=0, max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def full_amount(self) -> Decimal:
        return self.amount * self.quantity

    class Meta:
        verbose_name = 'Продукт заказа'
        verbose_name_plural = 'Продукты заказа'

    def __str__(self):
        return f'Объект заказа - {self.order}'
