from django.test import TestCase
from garpix_order.models.invoice import BaseInvoice
from garpix_order.models.order import BaseOrder
from django.contrib.auth import get_user_model
from garpix_order.models.order_item import BaseOrderItem
from django.core.exceptions import ValidationError


User = get_user_model()


OrderItemStatus = BaseOrderItem.OrderItemStatus


class PreBuildTestCase(TestCase):
    def setUp(self):
        self.data_user = {
            'username': 'test',
            'email': 'test@garpix.com',
            'password': 'BlaBla123',
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
        }
        self.user = User.objects.create_user(**self.data_user)
        self.order = BaseOrder.objects.create(number='test', user=self.user, total_amount=100)
        self.first_order_item = BaseOrderItem.objects.create(order=self.order, amount=25, quantity=2)
        self.two_order_item = BaseOrderItem.objects.create(order=self.order, amount=50, quantity=1)
        self.cancel_order_item = BaseOrderItem.objects.create(order=self.order, amount=100, quantity=2, status=OrderItemStatus.CANCELED)
        self.refund_order_item = BaseOrderItem.objects.create(order=self.order, amount=100, quantity=1, status=OrderItemStatus.REFUNDED)
        self.invoice = BaseInvoice.objects.create(title='test', order=self.order, amount=100)

    def test_order_full_payment(self):
        """Проверяем простую полную оплату"""
        self.invoice.succeeded()
        self.assertEqual(self.order.payed_amount, 100)
        print(self.order.status, 'self.order.status')
        self.assertEqual(self.order.status, BaseOrder.OrderStatus.PAYED_FULL)
        self.assertEqual(self.order.paid_items_amount(), 100)
        items = self.order.items_all()
        first_order_item = items[0]
        two_order_item = items[1]
        self.assertEqual(first_order_item.status, BaseOrderItem.OrderItemStatus.PAYED_FULL)
        self.assertEqual(two_order_item.status, BaseOrderItem.OrderItemStatus.PAYED_FULL)
        
    def test_order_partial_payment(self):
        """Проверяем оплату одного элемента"""
        self.invoice.succeeded(self.first_order_item)
        self.assertEqual(self.order.payed_amount, 50)
        two_invoice = BaseInvoice.objects.create(title='test', order=self.order, amount=50)
        two_invoice.succeeded(self.two_order_item)
        self.assertEqual(self.order.payed_amount, 100)

    def test_items_amount(self):
        """Проверка правильного подсчета суммы"""
        order = self.order
        self.assertEqual(order.items_amount(), 100)

    def test_order_item_full_amount(self):
        """Проверка правильного подсчета суммы одного элемента"""
        item = self.first_order_item
        self.assertEqual(item.full_amount(), 50)

    def test_invoice_zero(self):
        """Проверка что нельзя создать инвоис с 0"""
        invoice = BaseInvoice.objects.create(title='test', order=self.order, amount=0)
        self.assertRaises(ValidationError, invoice.clean)

    def test_invoice_amount_exceeds_order(self):
        """Проверка что нельзя создать инвоис больше общей суммы"""
        invoice = BaseInvoice.objects.create(title='test', order=self.order, amount=200)
        self.assertRaises(ValidationError, invoice.clean)

    def test_invoice_amount_exceeds_paid(self):
        """Проверка что нельзя создать инвоис больше оплаченной суммы"""
        order = BaseOrder.objects.create(number='test', user=self.user, payed_amount=50, total_amount=100)
        invoice = BaseInvoice.objects.create(title='test', order=order, amount=100)
        self.assertRaises(ValidationError, invoice.clean)
