from garpixcms.settings import *  # noqa

INSTALLED_APPS += [
    'garpix_order',
    'example',
    'fsm_admin'
]


CASH_PAYMENT = 'cash'

PAYMENT_TYPES = {
    CASH_PAYMENT: {
        'title': 'Cash',
        'class': 'example.providers.cash.Cash',
        'parameters': {}
    },
}

CHOICES_PAYMENT_TYPES = [(k, v['title']) for k, v in PAYMENT_TYPES.items()]

