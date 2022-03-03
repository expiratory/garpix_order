from django.http import JsonResponse
from ...models import CloudPaymentInvoice
from decimal import Decimal
from django.db import transaction


PAYMENT_STATUS_COMPLETED = CloudPaymentInvoice.PAYMENT_STATUS_COMPLETED
PAYMENT_STATUS_CANCELLED = CloudPaymentInvoice.PAYMENT_STATUS_CANCELLED
PAYMENT_STATUS_DECLINED = CloudPaymentInvoice.PAYMENT_STATUS_DECLINED


def callback(payment):
    if payment.status == PAYMENT_STATUS_COMPLETED:
        payment.succeeded()
    elif payment.status in (PAYMENT_STATUS_CANCELLED, PAYMENT_STATUS_DECLINED):
        payment.failed()


@transaction.atomic
def default_view(request):
    if request.method == 'post':
        try:
            payment = CloudPaymentInvoice.objects.get(order_number=request.POST.get('InvoiceId'))
            payment.status = CloudPaymentInvoice.MAP_STATUS[request.POST.get('Status')]
            payment.is_test = request.POST.get('TestMode') == '1'
            payment.transaction_id = request.POST.get('TransactionId')
            if payment.price != Decimal(request.POST.get('Amount')):
                raise Exception('Wrong price')
            payment.save()
            callback(payment)
        except CloudPaymentInvoice.DoesNotExist:
            return JsonResponse({"code": 1})
        except Exception:
            return JsonResponse({"code": 2})
    return JsonResponse({"code": 0})
