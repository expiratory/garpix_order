from django.db import models
from garpix_page.models import BasePage

from garpix_order.models import BaseOrder, BaseOrderItem


class ExamplePage(BasePage):
    template = "pages/example.html"

    class Meta:
        verbose_name = "Example"
        verbose_name_plural = "Examples"
        ordering = ("-created_at",)


class Order(BaseOrder):
    pass


class Service(BaseOrderItem):
    def pay(self):
        print('pay')
