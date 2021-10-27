from ..models.example_page import ExamplePage
from django.contrib import admin
from garpix_page.admin import BasePageAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from garpix_order.models import BaseOrder, BaseOrderItem, BaseInvoice
from ..models.example_page import Service, Order


@admin.register(ExamplePage)
class ExamplePageAdmin(BasePageAdmin):
    pass


@admin.register(Order)
class OrderAdmin(PolymorphicChildModelAdmin):
    child_models = ()


@admin.register(Service)
class ServiceAdmin(PolymorphicChildModelAdmin):
    child_models = ()


@admin.register(BaseOrder)
class BaseOrderAdmin(PolymorphicParentModelAdmin):
    base_model = BaseOrder
    child_models = (Order,)


@admin.register(BaseOrderItem)
class BaseOrderItemAdmin(PolymorphicParentModelAdmin):
    base_model = BaseOrderItem
    child_models = (Service,)


@admin.register(BaseInvoice)
class BaseInvoiceAdmin(PolymorphicParentModelAdmin):
    base_model = BaseInvoice
    child_models = (BaseInvoice,)
