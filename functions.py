import string


def contains_digits(word) -> bool:
    """ Вспомогательная функция для проверки строки на предмет наличия цифр"""
    # Проверка, содержит ли строка цифры
    for char in word:
        if char.isdigit():
            return True
    return False


def contains_only_latin_chars(input_str):
    """ Вспомогательная функция для проверки строки на предмет наличия букв на не латинице"""
    # Убедимся, что строка не пуста
    if not input_str:
        return False

    # Проверка, содержит ли строка только символы латинского алфавита
    return all(char in string.ascii_letters for char in input_str)
