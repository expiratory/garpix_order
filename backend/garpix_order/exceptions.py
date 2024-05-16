class BasePaymentException(Exception):
    pass


class UndefinedModelPaymentException(BasePaymentException):
    def __init__(self, message="Не задана модель-наследник BaseSberPayment в settings.py."):
        super().__init__(message)


class InvalidModelPaymentException(BasePaymentException):
    def __init__(self, message="Заданная модель для платежей Сбера не является наследником BaseSberPayment."):
        super().__init__(message)


class InvalidOrderStatusPaymentException(BasePaymentException):
    def __init__(self, message="Неподдерживаемый статус заказа."):
        super().__init__(message)
