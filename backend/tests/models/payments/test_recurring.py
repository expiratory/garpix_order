from django.utils import timezone
from app.tests import TestMixin
from garpix_order.models.payments.recurring import Recurring

class RecurringTestCase(TestMixin):

    def setUp(self):
        self.recurring_monthly = Recurring(
            start_at=timezone.datetime(2014, 1, 31),
            end_at=timezone.datetime(3014, 1, 31),
            frequency=Recurring.RecurringFrequency.MONTH,
            payment_system=Recurring.RecurringPaymentSystem.ROBOKASSA
        )

        self.recurring_yearly = Recurring(
            start_at=timezone.datetime(2014, 1, 31),
            end_at=timezone.datetime(3014, 1, 31),
            frequency=Recurring.RecurringFrequency.YEAR,
            payment_system=Recurring.RecurringPaymentSystem.ROBOKASSA
        )

    def test_get_next_payment_date_monthly(self):
        next_payment_date = self.recurring_monthly.get_next_payment_date()
        pass

    def test_get_next_payment_date_yearly(self):
        next_payment_date = self.recurring_yearly.get_next_payment_date()
        pass
