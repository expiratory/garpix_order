import json
from urllib import response
import uuid
from django.test import TestCase
from django_fsm import can_proceed
from garpix_order.models.payments.cloudpayments import CloudPaymentInvoice
from garpix_order.models.invoice import BaseInvoice
from garpix_order.models.order import BaseOrder
from django.contrib.auth import get_user_model
from garpix_order.models.order_item import BaseOrderItem
from rest_framework.test import APIClient


User = get_user_model()


OrderItemStatus = BaseOrderItem.OrderItemStatus
InvoiceStatus = BaseInvoice.InvoiceStatus


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
        client = APIClient()
        self.client = client

    def test_order_full_payment(self):
        """Проверяем простую полную оплату"""
        self.invoice.succeeded()
        self.assertEqual(self.order.payed_amount, 100)
        self.assertEqual(self.order.status, BaseOrder.OrderStatus.PAYED_FULL)
        self.assertEqual(self.order.paid_items_amount(), 100)
        items = self.order.items_all()
        first_order_item = items[0]
        two_order_item = items[1]
        self.assertEqual(first_order_item.status, BaseOrderItem.OrderItemStatus.PAYED_FULL)
        self.assertEqual(two_order_item.status, BaseOrderItem.OrderItemStatus.PAYED_FULL)
        
    def test_order_partial_payment(self):
        """Проверяем оплату одного элемента"""
        self.invoice.succeeded_partially(self.first_order_item)
        self.assertEqual(self.order.payed_amount, 50)
        two_invoice = BaseInvoice.objects.create(title='test', order=self.order, amount=50)
        two_invoice.succeeded_partially(self.two_order_item)
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
        self.assertFalse(can_proceed(invoice.succeeded))
        self.assertRaises(Exception, invoice.succeeded)

    def test_invoice_amount_exceeds_order(self):
        """Проверка что нельзя создать инвоис больше общей суммы"""
        invoice = BaseInvoice.objects.create(title='test', order=self.order, amount=200)
        self.assertFalse(can_proceed(invoice.succeeded))
        self.assertRaises(Exception, invoice.succeeded)

    def test_invoice_amount_exceeds_paid(self):
        """Проверка что нельзя создать инвоис больше оплаченной суммы"""
        order = BaseOrder.objects.create(number='test', user=self.user, payed_amount=50, total_amount=100)
        invoice = BaseInvoice.objects.create(title='test', order=order, amount=100)
        self.assertFalse(can_proceed(invoice.succeeded))
        self.assertRaises(Exception, invoice.succeeded)

    def test_order_full_refunded(self):
        """Проверяем простой полный возврат средств"""
        self.invoice.succeeded()
        invoice_refounted = BaseInvoice.objects.create(title='test', order=self.order, amount=100)
        invoice_refounted.refunded()
        items = self.order.items_all()
        first_order_item = items[0]
        two_order_item = items[1]
        self.assertEqual(first_order_item.status, BaseOrderItem.OrderItemStatus.REFUNDED)
        self.assertEqual(two_order_item.status, BaseOrderItem.OrderItemStatus.REFUNDED)
        self.assertEqual(self.order.payed_amount, 0)
        self.assertEqual(self.order.paid_items_amount(), 0)

    def test_refund_amount_check(self):
        #  Проверяем, что рефанд можно сделать только на оплаченный ордер
        invoice_refounted = BaseInvoice.objects.create(title='test', order=self.order, amount=100)
        self.assertFalse(can_proceed(invoice_refounted.refunded))
        self.assertRaises(Exception, invoice_refounted.refunded)

        self.invoice.succeeded()
        #  Проверяем, что рефанд можно сделать только на полную сумму
        invoice_refounted = BaseInvoice.objects.create(title='test', order=self.order, amount=99)
        self.assertFalse(can_proceed(invoice_refounted.refunded))
        self.assertRaises(Exception, invoice_refounted.refunded)

        invoice_refounted = BaseInvoice.objects.create(title='test', order=self.order, amount=101)
        self.assertFalse(can_proceed(invoice_refounted.refunded))
        self.assertRaises(Exception, invoice_refounted.refunded)

    def test_cloudpayment_api(self):
        total_amount = 100
        transaction_id = uuid.uuid4().hex
        order = BaseOrder.objects.create(number='test', user=self.user, total_amount=total_amount)
        BaseOrderItem.objects.create(order=order, amount=25, quantity=2)
        BaseOrderItem.objects.create(order=order, amount=50, quantity=1)

        order_number = f'{order.pk}_order_number'
        cloudpayment_invoice = CloudPaymentInvoice.objects.create(
            title=order_number,
            order_number=order_number,
            order=order,
            amount=total_amount,
        )
        response = self.client.post(
            '/cloudpayments/pay/',
            {
                'InvoiceId': order_number,
                'TestMode': '1',
                'Amount': total_amount,
                'TransactionId': transaction_id,
                'Status': CloudPaymentInvoice.PAYMENT_STATUS_COMPLETED
            },
            # format='json',
            # HTTP_ACCEPT='application/json'
        )

        content = json.loads(response.content)
        invoice = CloudPaymentInvoice.objects.get(pk=cloudpayment_invoice.pk)
        order = BaseOrder.objects.get(pk=order.pk)

        self.assertEqual(content, {'code': 0})
        self.assertEqual(invoice.status, InvoiceStatus.SUCCEEDED)
        self.assertEqual(order.payed_amount, 100)
        self.assertEqual(order.status, BaseOrder.OrderStatus.PAYED_FULL)
        self.assertEqual(order.paid_items_amount(), 100)
        items = order.items_all()
        first_order_item = items[0]
        two_order_item = items[1]
        self.assertEqual(first_order_item.status, BaseOrderItem.OrderItemStatus.PAYED_FULL)
        self.assertEqual(two_order_item.status, BaseOrderItem.OrderItemStatus.PAYED_FULL)
