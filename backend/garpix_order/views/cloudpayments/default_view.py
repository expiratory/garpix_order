from django.http import JsonResponse
from ...models import CloudPayment
from decimal import Decimal
from django.db import transaction


PAYMENT_STATUS_COMPLETED = CloudPayment.PAYMENT_STATUS_COMPLETED
PAYMENT_STATUS_CANCELLED = CloudPayment.PAYMENT_STATUS_CANCELLED
PAYMENT_STATUS_DECLINED = CloudPayment.PAYMENT_STATUS_DECLINED


@transaction.atomic
def default_view(request):
    if request.method == 'POST':
        try:
            payment = CloudPayment.objects.get(order_number=request.POST.get('InvoiceId'))
            status = request.POST.get('Status')
            payment.is_test = request.POST.get('TestMode') == '1'
            payment.transaction_id = request.POST.get('TransactionId')
            if payment.amount != Decimal(request.POST.get('Amount')):
                raise Exception('Wrong price')
            if status == PAYMENT_STATUS_COMPLETED:
                payment.succeeded()
            elif status in (PAYMENT_STATUS_CANCELLED, PAYMENT_STATUS_DECLINED):
                payment.failed()
            payment.save()
        except CloudPayment.DoesNotExist:
            return JsonResponse({"code": 1})
        except Exception:
            return JsonResponse({"code": 2})
    return JsonResponse({"code": 0})
