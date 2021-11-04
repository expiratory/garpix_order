```python
from garpix_order.models import BaseOrder, BaseOrderItem


class Order(BaseOrder):
    pass


class Service(BaseOrderItem):
    def pay(self):
        print('pay')
```

**BaseOrder** - основной класс заказа

**BaseOrderItem** - части заказа. В один заказ можно пложить несколько сущностей

`pay` - метод у BaseOrder вызовет у всех BaseOrderItem метод `pay`.

