from ..invoice import BaseInvoice


class CashInvoice(BaseInvoice):
    class Meta:
        verbose_name = 'Платеж наличкой'
        verbose_name_plural = 'Платежи наличкой'
