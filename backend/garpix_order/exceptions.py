class BasePaymentException(Exception):
    pass


class UndefinedModelForSberPaymentException(BasePaymentException):
    def __init__(self, message="Не задана модель-наследник BaseSberPayment в settings.py."):
        super().__init__(message)


class InvalidModelForSberPaymentException(BasePaymentException):
    def __init__(self, message="Заданная модель для платежей Сбера не является наследником BaseSberPayment."):
        super().__init__(message)
