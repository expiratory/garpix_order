from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GarpixOrderConfig(AppConfig):
    name = 'garpix_order'
    verbose_name = _('Order')
