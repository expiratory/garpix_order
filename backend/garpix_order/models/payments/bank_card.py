from ..payment import BasePayment


class BankCardPayment(BasePayment):
    class Meta:
        verbose_name = 'Платеж банковской картой'
        verbose_name_plural = 'Платежи банковской картой'
