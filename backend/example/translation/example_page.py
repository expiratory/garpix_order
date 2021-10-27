from modeltranslation.translator import TranslationOptions, register
from ..models import ExamplePage


@register(ExamplePage)
class ExamplePageTranslationOptions(TranslationOptions):
    pass
