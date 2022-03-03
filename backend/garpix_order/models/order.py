from django.db import models, transaction
from django.db.models import F, Sum, DecimalField
from polymorphic.models import PolymorphicModel
from django.conf import settings


class BaseOrder(PolymorphicModel):
    number = models.CharField(max_length=255, verbose_name='Номер заказа')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Пользователь")
    total_amount = models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Полная стоимость')
    payed_amount = models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Оплачено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def make_instance(self):
        pass

    def items(self):
        return self.baseorderitem_set.all()

    def items_amount(self):
        amount = self.items().aggregate(
            total=Sum(F('amount') * F('quantity'), output_field=DecimalField()))
        return amount.get('total', 0)

    @transaction.atomic
    def pay_full(self):
        for item in self.items():
            item.pay()
        self.payed_amount = self.total_amount
        self.save()

    def pay_partially(self, item):
        pass

    def cancel(self):
        pass

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Базовый ордер'
        verbose_name_plural = 'Базовые ордера'
        ordering = ('-created_at',)
