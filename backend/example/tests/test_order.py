from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Order, Service, Invoice


class OrderTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.username = 'testuser1'
        self.password = '12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.total_price = 1000
        self.quantity = 2
        self.order = Order.objects.create(number='#test', user=self.user, total_amount=self.total_price * self.quantity)
        self.service = Service.objects.create(order=self.order, amount=self.total_price, quantity=self.quantity)

    def test_amount(self):
        order = self.order
        self.assertEqual(order.items_amount(), self.total_price * self.quantity)

    def test_payfull(self):
        order = self.order
        invoice = Invoice.objects.create(title=f'order-{order.id}', order=order, amount=order.total_amount)
        invoice.pending()
        invoice.succeeded()
        self.assertEqual(order.payed_amount, self.total_price * self.quantity)
