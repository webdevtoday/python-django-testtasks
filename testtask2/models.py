from django.db import models


class Users(models.Model):
    referral_id = models.CharField(max_length=255, verbose_name='Referral ID')
    user_id = models.CharField(
        max_length=255, verbose_name='User ID', unique=True)
    username = models.CharField(max_length=20, verbose_name='Имя')
    time_create = models.DateTimeField(
        auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(
        auto_now=True, verbose_name='Время изменения')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ['-time_create', 'username']
