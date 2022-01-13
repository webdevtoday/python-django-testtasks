from django.core.management.base import BaseCommand
from django.conf import settings

from testtask1.services.PhoneService import is_valid_phone
from testtask1.services.OrderService import save_order
from testtask1.services.GoogleSheetsService import save_to_google_sheets

import re

import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CallbackContext,
    Updater,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


VARIANTS_LIST = ['Вариант №1', 'Вариант №2', 'Вариант №3']
WHITE_CHECK_MARK_EMOJI = u"\U00002705"
NAME_REGEX = r'^[A-Za-zА-Яа-я]{2,20}$'

ADDITIONAL_TEXT = {
    'name': '\n\nОбратите внимание на корректность имени! Корректное имя состоит только из букв.\nМинимальная длина имени 2 символа.',
    'phone': '\n\nОбратите внимание на корректность номера телефона! Корректный номер телефона состоит только из цифр.\nМинимальная длина номера телефона 10 символов.',
    'variants': '\n\nВы можете выбрать несколько вариантов. Отменить выбранный вариант можно нажав на него. Чтобы закончить выбирать варианты, нажмите кнопку "Закончить выбор"',
}

NAME, CHECK_NAME, PHONE, CHOOSING_VARIANTS = range(4)
END = ConversationHandler.END


def start(update: Update, context: CallbackContext):
    text = (
        "Вас приветствует Бот!"
        "Пройдите анкету, пожалуйста!"
        "\n\nОстановить прохождение анкеты можно в любой момент командой /stop"
    )

    buttons = [[InlineKeyboardButton(
        text='Пройти анкету',
        callback_data=str(NAME)
    )]]

    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(
        text=text, reply_markup=keyboard)

    return NAME


def name(update: Update, context: CallbackContext):
    text = 'Введите Ваше имя, пожалуйста!' + ADDITIONAL_TEXT['name']

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return CHECK_NAME


def check_name(update: Update, context: CallbackContext):
    name = update.message.text
    context.user_data['name'] = name

    if not re.match(NAME_REGEX, name):
        update.message.reply_text(
            text=(
                "Вы ввели:\n"
                f"Имя: {name}\n\n"
                f"Введённое имя: ( {name} ), не корректное."
                "Пожалуйста, введите корректное имя!" + ADDITIONAL_TEXT['name']
            ),
        )
        return None

    update.message.reply_text(
        text=(
            f'Вы ввели:\n'
            f'Имя: {name}\n\n'
            'Введите Ваш номер телефона, пожалуйста!' +
            ADDITIONAL_TEXT['phone']
        ),
    )

    return PHONE


def phone(update: Update, context: CallbackContext):
    phone = update.message.text
    context.user_data['phone'] = phone
    name = context.user_data['name']

    if not is_valid_phone(phone):
        update.message.reply_text(
            text=(
                "Вы ввели:\n"
                f"Имя: {name}\n"
                f"Номер телефона: {phone}\n\n"
                f"Введённый номер телефона: ( {phone} ), не корректный."
                "Пожалуйста, введите корректный номер!" +
                ADDITIONAL_TEXT['phone']
            ),
        )
        return None

    context.user_data['variants'] = []

    keyboard = InlineKeyboardMarkup(
        create_variants_buttons(context.user_data['variants']))

    update.message.reply_text(
        text=(
            'Вы ввели:\n'
            f'Имя: {name}\n'
            f'Номер телефона: {phone}\n\n'
            'Выберите вариант(ы):' + ADDITIONAL_TEXT['variants']
        ),
        reply_markup=keyboard
    )

    return CHOOSING_VARIANTS


def create_variants_buttons(variants):
    buttons = []

    for i in range(len(VARIANTS_LIST)):
        text = VARIANTS_LIST[i]

        if i in variants:
            text = WHITE_CHECK_MARK_EMOJI + ' ' + VARIANTS_LIST[i]

        buttons.append([InlineKeyboardButton(text=text, callback_data=str(i))])

    if variants:
        buttons.append([InlineKeyboardButton(
            text='Закончить выбор',
            callback_data=str(len(VARIANTS_LIST) + 1)
        )])

    return buttons


def get_variants_by_index(selected_variants):
    variants = []
    for var in selected_variants:
        variants.append(VARIANTS_LIST[int(var)])
    return variants


def choosing_variants(update: Update, context: CallbackContext):
    name = context.user_data['name']
    phone = context.user_data['phone']
    variant = int(update.callback_query.data)

    if variant in context.user_data['variants']:
        context.user_data['variants'].remove(variant)
    else:
        context.user_data['variants'].append(variant)

    keyboard = InlineKeyboardMarkup(
        create_variants_buttons(context.user_data['variants']))

    variants = get_variants_by_index(context.user_data['variants'])

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=(
            'Вы ввели:\n'
            f'Имя: {name}\n'
            f'Номер телефона: {phone}\n'
            'Выбранные варианты: ' + ', '.join(variants) +
            '\n\nВыберите вариант(ы):' + ADDITIONAL_TEXT['variants']
        ),
        reply_markup=keyboard
    )

    return None


def finish(update: Update, context: CallbackContext):
    data = context.user_data

    variants = get_variants_by_index(data['variants'])

    update.callback_query.answer()
    text = (
        'Спасибо за внимание!\n\n'
        'Вы ввели:\nИмя:' + data['name'] +
        '\nНомер телефона: ' + data['phone'] +
        '\nВарианты: ' + ', '.join(variants)
    )
    update.callback_query.edit_message_text(text=text)

    order_obj = {
        'chat_id': update.effective_chat.id,
        'telegram_login': update.effective_user.username,
        'name': data['name'],
        'phone': data['phone'],
        'variants': ','.join(variants),
    }

    save_order(order_obj)
    save_to_google_sheets(order_obj)

    return END


def stop(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Вы прекратили прохождения анкеты'
        'чтобы начать прохождение анкеты используйте команду /start'
    )
    return END


class Command(BaseCommand):
    help = 'Тестовое задание №1'

    def handle(self, *args, **kwargs):
        updater = Updater(token=settings.TOKEN)
        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', start)
            ],
            states={
                NAME: [
                    CallbackQueryHandler(name, pattern='^' + str(NAME) + '$'),
                    CommandHandler('stop', stop),
                ],
                CHECK_NAME: [
                    MessageHandler(Filters.text & ~
                                   Filters.command, check_name),
                    CommandHandler('stop', stop),
                ],
                PHONE: [
                    MessageHandler(Filters.text & ~Filters.command, phone),
                    CommandHandler('stop', stop),
                ],
                CHOOSING_VARIANTS: [
                    CallbackQueryHandler(
                        choosing_variants, pattern='^' + '|'.join([str(i) for i in range(len(VARIANTS_LIST))]) + '$'),
                    CallbackQueryHandler(
                        finish, pattern='^' + str(len(VARIANTS_LIST)+1) + '$'),
                    CommandHandler('stop', stop),
                ],
            },
            fallbacks=[CommandHandler('stop', stop)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
