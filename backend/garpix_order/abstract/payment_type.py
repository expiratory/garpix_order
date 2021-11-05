class BasePaymentType:
    @staticmethod
    def pay(invoice):
        raise NotImplementedError

    @staticmethod
    def refund(invoice):
        raise NotImplementedError

    @staticmethod
    def cancel(invoice):
        raise NotImplementedError

    @staticmethod
    def check_status(invoice):
        raise NotImplementedError
