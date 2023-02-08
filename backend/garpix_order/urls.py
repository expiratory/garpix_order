from django.urls import path
from .views.cloudpayments import CloudpaymentView

urlpatterns = [
    path('cloudpayments/pay/', CloudpaymentView.pay_view),
    path('cloudpayments/fail/', CloudpaymentView.fail_view),
    path('cloudpayments/payment_data/', CloudpaymentView.payment_data_view),
]
