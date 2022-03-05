from ..payment import BasePayment


class CashPayment(BasePayment):
    class Meta:
        verbose_name = 'Платеж наличкой'
        verbose_name_plural = 'Платежи наличкой'
