from django.conf import settings
import urllib.parse
import requests


def save_to_google_sheets(order):
    chat_id = urllib.parse.quote(str(order["chat_id"]))
    tg_login = urllib.parse.quote(str(order["telegram_login"]))
    name = urllib.parse.quote(str(order["name"]))
    phone = urllib.parse.quote(str(order["phone"]))
    variants = urllib.parse.quote(str(order["variants"]))
    
    requests.get(
        settings.GOOGLE_SHEETS_LINK +
        f"?chat_id={chat_id}"
        f"&tg_login={tg_login}"
        f"&name={name}"
        f"&phone={phone}"
        f"&variants={variants}"
    )

    return
