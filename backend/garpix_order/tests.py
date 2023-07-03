import json
import uuid
from django.test import TestCase
from django_fsm import can_proceed
from garpix_order.models.payments.cash import CashPayment
from garpix_order.models.payments.cloudpayments import CloudPayment
from garpix_order.models.payment import BasePayment
from garpix_order.models.order import BaseOrder
from django.contrib.auth import get_user_model
from garpix_order.models.order_item import BaseOrderItem
from rest_framework.test import APIClient


User = get_user_model()


PaymentStatus = BasePayment.PaymentStatus


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
        self.payment = self.order.make_full_payment(title='test payment')
        client = APIClient()
        self.client = client

    def test_order_full_payment(self):
        """Проверяем простую полную оплату"""
        self.payment.succeeded()
        self.assertEqual(self.order.payed_amount, 100)
        self.assertEqual(self.order.status, BaseOrder.OrderStatus.PAYED_FULL)
        
    def test_order_partial_payment(self):
        """Проверяем оплату одного элемента"""
        payment = BasePayment.objects.create(title='test', order=self.order, amount=50)
        payment.succeeded()
        payment.save()
        order = BaseOrder.objects.get(pk=self.order.pk)
        self.assertEqual(order.payed_amount, 50)
        self.assertEqual(order.status, BaseOrder.OrderStatus.PAYED_PARTIAL)

        two_payment = BasePayment.objects.create(title='test', order=self.order, amount=50)
        two_payment.succeeded()
        two_payment.save()
        order = BaseOrder.objects.get(pk=self.order.pk)
        self.assertEqual(order.payed_amount, 100)
        self.assertEqual(order.status, BaseOrder.OrderStatus.PAYED_FULL)

    def test_order_item_full_amount(self):
        """Проверка правильного подсчета суммы одного элемента"""
        item = self.first_order_item
        self.assertEqual(item.full_amount(), 50)

    def test_payment_zero(self):
        """Проверка что нельзя создать инвоис с 0"""
        payment = BasePayment.objects.create(title='test', order=self.order, amount=0)
        self.assertFalse(can_proceed(payment.succeeded))
        self.assertRaises(Exception, payment.succeeded)

    def test_payment_amount_exceeds_order(self):
        """Проверка что нельзя создать инвоис больше общей суммы"""
        payment = BasePayment.objects.create(title='test', order=self.order, amount=200)
        self.assertFalse(can_proceed(payment.succeeded))
        self.assertRaises(Exception, payment.succeeded)

    def test_payment_amount_exceeds_paid(self):
        """Проверка что нельзя создать инвоис больше оплаченной суммы"""
        order = BaseOrder.objects.create(number='test', user=self.user, payed_amount=50, total_amount=100)
        payment = BasePayment.objects.create(title='test', order=order, amount=100)
        self.assertFalse(can_proceed(payment.succeeded))
        self.assertRaises(Exception, payment.succeeded)

    def test_order_full_refunded(self):
        """Проверяем простой полный возврат средств"""
        payment = BasePayment.objects.create(title='test', order=self.order, amount=100)
        payment.succeeded()
        payment_refounted = BasePayment.make_refunded(payment)
        payment_refounted.refunded()
        order = BaseOrder.objects.get(pk=self.order.pk)
        self.assertEqual(order.payed_amount, 0)
        self.assertEqual(order.status, BaseOrder.OrderStatus.REFUNDED)

    def test_order_partial_refunded(self):
        """Возвращает оплату частями"""
        order = BaseOrder.objects.create(number='test', user=self.user, total_amount=100)
        payment = BasePayment.objects.create(title='test', order=order, amount=50)
        payment.succeeded()
        payment.save()

        two_payment = BasePayment.objects.create(title='test', order=order, amount=50)
        two_payment.succeeded()
        payment.save()

        payment_refounted_first = BasePayment.make_refunded(payment)
        payment_refounted_first.refunded()
        payment_refounted_first.save()
        self.assertEqual(order.payed_amount, 50)
        self.assertEqual(order.status, BaseOrder.OrderStatus.PAYED_PARTIAL)

        payment_refounted_two = BasePayment.make_refunded(two_payment)
        payment_refounted_two.refunded()
        payment_refounted_two.save()
        self.assertEqual(order.payed_amount, 0)
        self.assertEqual(order.status, BaseOrder.OrderStatus.REFUNDED)

    def test_refund_amount_check(self):
        """Проверяем, что рефанд можно сделать только на оплаченный ордер"""
        payment = BasePayment.objects.create(title='test', order=self.order, amount=100)
        payment_refounted = BasePayment.make_refunded(payment)
        self.assertFalse(can_proceed(payment_refounted.refunded))
        self.assertRaises(Exception, payment_refounted.refunded)

    def test_cloudpayment_api(self):
        total_amount = 100
        transaction_id = uuid.uuid4().hex
        order = BaseOrder.objects.create(number='test', user=self.user, total_amount=total_amount)
        BaseOrderItem.objects.create(order=order, amount=25, quantity=2)
        BaseOrderItem.objects.create(order=order, amount=50, quantity=1)

        order_number = f'{order.pk}_order_number'
        cloudpayment_payment = CloudPayment.objects.create(
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
                'Status': CloudPayment.PAYMENT_STATUS_COMPLETED
            },
            # format='json',
            # HTTP_ACCEPT='application/json'
        )

        content = json.loads(response.content)
        payment = CloudPayment.objects.get(pk=cloudpayment_payment.pk)
        order = BaseOrder.objects.get(pk=order.pk)

        self.assertEqual(content, {'code': 0})
        self.assertEqual(payment.status, PaymentStatus.SUCCEEDED)
        self.assertEqual(order.payed_amount, 100)
        self.assertEqual(order.status, BaseOrder.OrderStatus.PAYED_FULL)

    def test_split_order(self):
        order = BaseOrder.objects.create(number='test', user=self.user, total_amount=100)
        first_order_item = BaseOrderItem.objects.create(order=order, amount=25, quantity=3)
        BaseOrderItem.objects.create(order=order, amount=25, quantity=1)

        new_order = BaseOrder.split_order(number='new_order', item=first_order_item)

        order = BaseOrder.objects.get(pk=order.pk)
        self.assertEqual(order.total_amount, 25)
        self.assertEqual(new_order.total_amount, 75)
