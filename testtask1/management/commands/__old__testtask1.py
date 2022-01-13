from django.core.management.base import BaseCommand
from django.conf import settings
from testtask1.models import Order

import requests
import urllib.parse

import re

import phonenumbers

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

emoji = {
    'white_check_mark': u"\U00002705"
}

NAME, CHECK_NAME, PHONE, CHOOSING_VARIANTS = range(4)
END = ConversationHandler.END

VARIANTS_LIST = [
    'Вариант №1', 'Вариант №2', 'Вариант №3'
]

ADDITIONAL_TEXT = {
    'correct_name': '\n\nОбратите внимание на корректность имени! Корректное имя состоит только из букв.\nМинимальная длина имени 2 символа.',
    'correct_phone': '\n\nОбратите внимание на корректность номера телефона! Корректный номер телефона состоит только из цифр.\nМинимальная длина номера телефона 10 символов.',
    'correct_variants': '\n\nВы можете выбрать несколько вариантов. Отменить выбранный вариант можно нажав на него. Чтобы закончить выбирать варианты, нажмите кнопку "Закончить выбор"',
}

REGEX = {
    'name': r'^[A-Za-zА-Яа-я]{2,20}$',
}


def start(update: Update, context: CallbackContext):
    text = "Вас приветствует Бот! Пройдите анкету, пожалуйста!\n\nОстановить прохождение анкеты можно в любой момент командой /stop"

    buttons = [[InlineKeyboardButton(
        text='Пройти анкету',
        callback_data=str(NAME)
    )]]

    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(
        text=text, reply_markup=keyboard)

    return NAME


def name(update: Update, context: CallbackContext):
    text = 'Введите Ваше имя, пожалуйста!' + ADDITIONAL_TEXT['correct_name']

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return CHECK_NAME


def check_name(update: Update, context: CallbackContext):
    name = update.message.text
    context.user_data['name'] = name

    if not re.match(REGEX['name'], name):
        update.message.reply_text(
            text=f"Вы ввели:\nИмя: {name}\n\nВведённое имя: ( {name} ), не корректное. Пожалуйста, введите корректное имя!" +
            ADDITIONAL_TEXT['correct_name'],
        )
        return None

    update.message.reply_text(
        text=f'Вы ввели:\nИмя: {name}\n\nВведите Ваш номер телефона, пожалуйста!' +
        ADDITIONAL_TEXT['correct_phone'],
    )

    return PHONE


def isValidPhone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, 'UA')
        is_valid_phone = phonenumbers.is_valid_number(parsed_phone)
        if not is_valid_phone:
            return False
        return True
    except:
        return False


def phone(update: Update, context: CallbackContext):
    phone = update.message.text
    context.user_data['phone'] = phone
    name = context.user_data['name']

    if not isValidPhone(phone):
        update.message.reply_text(
            text=f"Вы ввели:\nИмя: {name}\nНомер телефона: {phone}\n\nВведённый номер телефона: ( {phone} ), не корректный. Пожалуйста, введите корректный номер!" +
            ADDITIONAL_TEXT['correct_phone'],
        )
        return None

    context.user_data['variants'] = []

    keyboard = InlineKeyboardMarkup(
        create_variants_buttons(context.user_data['variants']))

    update.message.reply_text(
        text=f'Вы ввели:\nИмя: {name}\nНомер телефона: {phone}\n\nВыберите вариант(ы):' +
        ADDITIONAL_TEXT['correct_variants'],
        reply_markup=keyboard
    )

    return CHOOSING_VARIANTS


def create_variants_buttons(variants):
    buttons = []

    for i in range(len(VARIANTS_LIST)):
        if i in variants:
            buttons.append([InlineKeyboardButton(
                text=emoji['white_check_mark'] + ' ' + VARIANTS_LIST[i], callback_data=str(i))])
        else:
            buttons.append([InlineKeyboardButton(
                text=VARIANTS_LIST[i], callback_data=str(i))])

    if variants:
        buttons.append([InlineKeyboardButton(
            text='Закончить выбор',
            callback_data=str(len(VARIANTS_LIST) + 1)
        )])

    return buttons


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

    variants = []
    for var in context.user_data['variants']:
        variants.append(VARIANTS_LIST[int(var)])

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=f'Вы ввели:\nИмя: {name}\nНомер телефона: {phone}\nВыбранные варианты: ' +
        ', '.join(variants) + '\n\nВыберите вариант(ы):' +
        ADDITIONAL_TEXT['correct_variants'],
        reply_markup=keyboard
    )

    return None


def save_to_db(order):
    order = Order(
        chat_id=order["chat_id"],
        login=order["telegram_login"],
        name=order["name"],
        phone=order["phone"],
        variants=order["variants"],
    )
    order.save()
    return


def save_to_google_sheets(order):
    chat_id = urllib.parse.quote(str(order["chat_id"]))
    tg_login = urllib.parse.quote(str(order["telegram_login"]))
    name = urllib.parse.quote(str(order["name"]))
    phone = urllib.parse.quote(str(order["phone"]))
    variants = urllib.parse.quote(str(order["variants"]))

    res = requests.get(
        f"https://script.google.com/macros/s/AKfycbxZNI9AY_Ihxzjmn_qgBv7WYTU4X3XAJg1R196qoHjub9r5sifnqevT3L4RP-0hbiBmbQ/exec?chat_id={chat_id}&tg_login={tg_login}&name={name}&phone={phone}&variants={variants}")

    return


def finish(update: Update, context: CallbackContext):
    data = context.user_data

    variants = []
    for var in data['variants']:
        variants.append(VARIANTS_LIST[int(var)])

    update.callback_query.answer()
    text = 'Спасибо за внимание!\n\nВы ввели:\nИмя:' + \
        data['name'] + '\nНомер телефона: ' + data['phone'] + \
        '\nВарианты: ' + ', '.join(variants)
    update.callback_query.edit_message_text(text=text)

    order_obj = {
        'chat_id': update.effective_chat.id,
        'telegram_login': update.effective_user.username,
        'name': data['name'],
        'phone': data['phone'],
        'variants': ','.join(variants),
    }

    save_to_db(order_obj)
    save_to_google_sheets(order_obj)

    return END


def stop(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Вы прекратили прохождения анкеты, чтобы начать прохождение анкеты используйте команду /start')
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
