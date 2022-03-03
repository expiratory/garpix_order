from django.http import JsonResponse
from ...models import Config
from ...models import CloudPaymentInvoice


def payment_data_view(request):
    config = Config.get_solo()
    payment_uuid = request.GET.get('payment_uuid')
    try:
        payment = CloudPaymentInvoice.objects.get(payment_uuid=payment_uuid)
        return JsonResponse({
            'publicId': config.cloudpayments_public_id,
            'description': 'Оплата товара',
            'amount': payment.price,
            'currency': 'RUB',
            'invoiceId': payment.order_number,
            'skin': "mini",
        })
    except CloudPaymentInvoice.DoesNotExist:
        return JsonResponse({
            'error': 'Does not exist',
        })
