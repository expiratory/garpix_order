from django.urls import path
from .views.cloudpayments.pay import pay_view
from .views.cloudpayments.fail import fail_view
from .views.cloudpayments.payment_data import payment_data_view

urlpatterns = [
    path('cloudpayments/pay/', pay_view),
    path('cloudpayments/fail/', fail_view),
    path('cloudpayments/payment_data/', payment_data_view),
]
