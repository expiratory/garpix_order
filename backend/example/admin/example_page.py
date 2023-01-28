from ..models.example_page import ExamplePage
from django.contrib import admin
from garpix_page.admin import BasePageAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from garpix_order.models import BaseOrder, BaseOrderItem, BasePayment
from ..models.example_page import Service, Order, Invoice
from fsm_admin.mixins import FSMTransitionMixin


@admin.register(ExamplePage)
class ExamplePageAdmin(BasePageAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(FSMTransitionMixin, admin.ModelAdmin):
    readonly_fields = ('status',)
    fsm_field = ('status',)
    child_models = ()


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


@admin.register(BasePayment)
class BasePaymentAdmin(PolymorphicParentModelAdmin, FSMTransitionMixin, admin.ModelAdmin):
    fsm_field = ('status',)
    readonly_fields = ('status',)
    base_model = BasePayment
    child_models = (Invoice,)
