import phonenumbers


def is_valid_phone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, 'UA')
        is_valid_phone = phonenumbers.is_valid_number(parsed_phone)
        if not is_valid_phone:
            return False
        return True
    except:
        return False
