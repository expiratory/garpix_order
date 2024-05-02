from django.db import models
from django.utils.translation import gettext_lazy as _

from ..payment import BasePayment


class SberPaymentStatus:
    WITHOUT_STATUS = -1
    PENDING = 0
    WAITING_FOR_CAPTURE = 1
    FULL_PAID = 2
    CANCELLED = 3
    REFUNDED = 4
    AUTHORIZATION_THROUGH_ACS = 5
    DECLINED = 6

    SBER_PAYMENT_STATUS_CHOICES = (
        (PENDING, 'Заказ зарегистрирован, но не оплачен'),
        (WAITING_FOR_CAPTURE, 'Предавторизованная сумма захолдирована (для двухстадийных платежей)'),
        (FULL_PAID, 'Проведена полная авторизация суммы заказа'),
        (CANCELLED, 'Авторизация отменена'),
        (REFUNDED, 'По транзакции была проведена операция возврата'),
        (AUTHORIZATION_THROUGH_ACS, 'Инициирована авторизация через ACS банка-эмитента'),
        (DECLINED, 'Авторизация отклонена'),
    )


class SberPayment(BasePayment):
    sber_payment_status = models.IntegerField(
        verbose_name=_('Статус платежа в Сбере'),
        choices=SberPaymentStatus.SBER_PAYMENT_STATUS_CHOICES,
        default=SberPaymentStatus.WITHOUT_STATUS
    )
    external_payment_id = models.CharField(
        max_length=255,
        verbose_name=_('Внешний идентификатор платежа'),
        default='',
    )
    payment_link = models.CharField(
        max_length=255,
        verbose_name=_('Ссылка на оплату'),
        default='',
    )

    class Meta:
        verbose_name = _('Платеж в Сбере')
        verbose_name_plural = _('Платежи в Сбере')
