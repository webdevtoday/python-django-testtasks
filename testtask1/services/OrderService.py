from testtask1.models import Order

def save_order(order):
    order = Order(
        chat_id=order["chat_id"],
        login=order["telegram_login"],
        name=order["name"],
        phone=order["phone"],
        variants=order["variants"],
    )
    order.save()
    return