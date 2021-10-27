from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ExampleConfig(AppConfig):
    name = 'example'
    verbose_name = _('Example')
