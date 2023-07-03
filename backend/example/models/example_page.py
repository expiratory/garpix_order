from django.db import models
from garpix_page.models import BasePage
from garpix_order.models import BaseOrder, BaseOrderItem, BasePayment


class ExamplePage(BasePage):
    template = "pages/example.html"

    class Meta:
        verbose_name = "Example"
        verbose_name_plural = "Examples"
        ordering = ("-created_at",)


class Order(BaseOrder):
    class Meta:
        verbose_name = 'Ордер'
        verbose_name_plural = 'Ордера'


class Service(BaseOrderItem):
    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')

    def pay(self):
        self.is_paid = True
        self.save()

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class Invoice(BasePayment):
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
