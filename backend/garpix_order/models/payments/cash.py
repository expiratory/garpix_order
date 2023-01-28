from ..payment import BasePayment


class CashPayment(BasePayment):
    class Meta:
        verbose_name = 'Платеж наличными'
        verbose_name_plural = 'Платежи наличными'
