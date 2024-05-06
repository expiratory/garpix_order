# Garpix Order

```python
from garpix_order.models import BaseOrder, BaseOrderItem, BasePayment


class Order(BaseOrder):
    pass


class Service(BaseOrderItem):
    def pay(self):
        pass


class Invoice(BasePayment):
    pass
```

**BaseOrder** - основной класс заказа.

`items` - метод для получения связанных OrderItem.

`items_amount` - метод для получения суммы оплаты.

**BaseOrderItem** - части заказа. В один заказ можно положить несколько сущностей.

`pay` - метод вызовет у всех BaseOrderItem, когда оплачивается заказ.

`full_amount` - метод возвращает полную сумма заказа. 

**Invoice** - Основная модель для отслеживания статуса оплаты (транзакция). Содержит `status` с типом FSM.

## Эквайринг Сбер

**BaseSberPayment** Абстрактная модель для платежей Сбера. **Для работы необходимо** создать свою модель-наследник,
затем указать путь до нее в settings.py, например:
```python
SBER_PAYMENT_MODEL = 'path.to.your.app.models.SberPaymentModel'
```

Методы для создания платежа, получение его данных от провайдера и callback
находятся в garpix_order.services.sber.SberService.

### Логирование ошибок при запросах к эквайрингу (на данный момент поддерживается только в SberService)

Пример добавления логирования в settings.py с использованием библиотеки python-json-logger:

```commandline
pip install python-json-logger
```

```python
from garpix_order.logging.filters import PaymentAuthDataFilter


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "payment_auth_data_filter": {
            "()": PaymentAuthDataFilter,
        }
    },
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(message)s %(module)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
            "filters": ["payment_auth_data_filter"],
        }
    },
    "loggers": {"garpix_order.services.sber": {"handlers": ["stdout"], "level": "INFO", "propagate": False}},
}
```
