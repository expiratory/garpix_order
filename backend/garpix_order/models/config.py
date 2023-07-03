from django.db import models
from solo.models import SingletonModel


class Config(SingletonModel):
    cloudpayments_public_id = models.CharField(max_length=200, verbose_name='publicId из личного кабинета CP')

    def __str__(self):
        return 'Настройки'
