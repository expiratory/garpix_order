from ..invoice import BaseInvoice


class RobokassaInvoice(BaseInvoice):

    class Meta:
        verbose_name = 'Платеж Robokassa'
        verbose_name_plural = 'Платежи Robokassa'
