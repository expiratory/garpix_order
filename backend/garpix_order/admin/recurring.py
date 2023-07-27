from django.contrib import admin

from garpix_order.models.payments.recurring import Recurring


@admin.register(Recurring)
class RecurringAdmin(admin.ModelAdmin):
    readonly_fields = ('last_payment_at',)
