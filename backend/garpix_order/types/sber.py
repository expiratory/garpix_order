from decimal import Decimal
from typing import TypedDict

from ..models.order import BaseOrder


class CreatePaymentData(TypedDict, total=False):
    token: str  # Токен магазина
    orderNumber: str  # Номер (идентификатор) заказа в системе магазина.
    amount: int  # Сумма платежа в копейках.
    returnUrl: str  # URL перенаправления пользователя в случае успешной оплаты.


class GetPaymentData(TypedDict, total=False):
    token: str  # Токен магазина
    orderId: str  # Номер (идентификатор) заказа в системе магазина.


class PaymentCreationData(TypedDict):
    order: BaseOrder
    amount: Decimal
    external_payment_id: str
    payment_link: str
    client_data: str
    provider_data: str
    title: str


class FailedPaymentCreationData(TypedDict):
    order: BaseOrder
    amount: Decimal
    client_data: str
    provider_data: str
    title: str
