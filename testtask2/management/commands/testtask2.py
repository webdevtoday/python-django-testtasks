from django.core.management.base import BaseCommand
from django.conf import settings

from testtask2.models import *

import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
    Updater,
    CommandHandler,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    text = "Вы не можете начать использовать бот без реферальной ссылки. Перейдите в бот с помощью реферальной ссылки"

    if len(context.args) >= 1:
        referral_id = context.args[0]
        if Users.objects.filter(referral_id=referral_id).exists():
            user = Users.objects.filter(referral_id=referral_id).get()
            name = user.username
            user_id = user.user_id
            text = f"Приветствую {name}! Твой уникальный код - {user_id}"
        else:
            text = "Ваша реферальная ссылка не действительна"

    update.message.reply_text(text=text)


class Command(BaseCommand):
    help = 'Тестовое задание №1'

    def handle(self, *args, **kwargs):
        updater = Updater(token=settings.TOKEN)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))

        updater.start_polling()
        updater.idle()
