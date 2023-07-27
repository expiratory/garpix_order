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
