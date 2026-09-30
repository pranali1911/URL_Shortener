CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(number):
    if number == 0:
        return "0"

    result = ""

    while number > 0:
        number, remainder = divmod(number, 62)
        result = CHARACTERS[remainder] + result

    return result