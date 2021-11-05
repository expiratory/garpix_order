# Garpix Order

```python
from garpix_order.models import BaseOrder, BaseOrderItem, BaseInvoice


class Order(BaseOrder):
    pass


class Service(BaseOrderItem):
    def pay(self):
        pass


class Invoice(BaseInvoice):
    pass
```

**BaseOrder** - основной класс заказа.

`items` - метод для получения связанных OrderItem.

`items_amount` - метод для получения суммы оплаты.

**BaseOrderItem** - части заказа. В один заказ можно положить несколько сущностей.

`pay` - метод вызовет у всех BaseOrderItem, когда оплачивается заказ.

`full_amount` - метод возвращает полную сумма заказа. 

**Invoice** - Основная модель для отслеживания статуса оплаты (транзакция). Содержит `status` с типом FSM.

**BasePaymentType** - Абстрактная модель PaymentType для наследования в целях создания модели способа оплаты используемого в проекте.

Определившись с используемыми способами оплаты указываем их в settings.py
```
CASH_PAYMENT = 'cash'
CUSTOM_PAYMENT = 'custom'

PAYMENT_TYPES = {               
    CASH_PAYMENT: {                                           
        'title': 'Cash',                                
        'class': 'path.to.payment.class.CustomPayment',      
        'parameters': {}                                
    },
    CUSTOM_PAYMENT: {                                           
        'title': 'CUSTOM PAYMENT',                                
        'class': 'path.to.payment.class.CustomPayment',      
        'parameters': {}                                
    },
}
```