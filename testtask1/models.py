from django.db import models


class Order(models.Model):
    chat_id = models.CharField(max_length=255, verbose_name='Чат ID')
    login = models.CharField(max_length=255, verbose_name='Telegram логин')
    name = models.CharField(max_length=20, verbose_name='Имя')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    variants = models.TextField(verbose_name='Варианты')
    time_create = models.DateTimeField(
        auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(
        auto_now=True, verbose_name='Время изменения')

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = 'Заявки'
        verbose_name_plural = 'Заявки'
        ordering = ['-time_create', 'login']
