from django.db import models
from polymorphic.models import PolymorphicModel
from .order import BaseOrder


class BaseOrderItem(PolymorphicModel):
    order = models.ForeignKey(BaseOrder, on_delete=models.CASCADE, verbose_name="Заказ")
    amount = models.DecimalField(verbose_name='Цена', default=0, max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def full_amount(self):
        return self.price * self.quantity

    def pay(self):
        raise NotImplementedError('payment not implemented')

    class Meta:
        verbose_name = 'Продукт заказа'
        verbose_name_plural = 'Продукты заказа'

    def __str__(self):
        return f'Объект заказа {self.order}'
