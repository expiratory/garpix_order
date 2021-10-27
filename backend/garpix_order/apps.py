from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OrderConfig(AppConfig):
    name = 'garpix_order'
    verbose_name = _('Order')
