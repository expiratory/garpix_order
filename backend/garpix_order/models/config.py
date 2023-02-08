from django.db import models
from solo.models import SingletonModel


class Config(SingletonModel):
    cloudpayments_public_id = models.CharField(max_length=200, verbose_name='publicId из личного кабинета CloudPayments')
    cloudpayments_password_api = models.CharField(max_length=200, default='', verbose_name='Пароль для API из личного кабинета CloudPayments')

    def __str__(self):
        return 'Настройки'
