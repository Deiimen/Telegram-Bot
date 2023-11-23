from config import API_KEY, BASE_URL
import requests


def get_langs():
    """ Функция получения JSON словаря с перечнем направлений перевода"""
    response = requests.get(f'{BASE_URL}/getLangs', params={
        'key': API_KEY
    })
    return response


def lookup(text, lang='en-ru', ui='ru'):
    """ Функция получения JSON словаря с полной информацией по введенному слову от пользователя"""
    response = requests.get(f'{BASE_URL}/lookup', params={
        'key': API_KEY,
        'lang': lang,
        'text': text,
        'ui': ui
    })
    return response


def yandex_translate(text):
    """ Функция получат на ввод слово Str и при помощи вспомогательных
    функций получает JSON словарь и возвращает список переведенный слов
    """
    # Получаем объект
    langs_response = get_langs()

    # Проверка запроса по получению словаря направления перевода JSON на предмет кода 200
    if langs_response.status_code != 200:
        print('Не удалось получить список направлений перевода')
        exit(1)

    # Проверка запроса по получению словаря полной информации о слове JSON на предмет кода 200
    lookup_response = lookup(text)
    if lookup_response.status_code != 200:
        exit(1)

    result = []
    # Берем из JSON только перевод на рус., без синонимов и др. лишней инфо
    for i_elem in lookup_response.json()['def']:
        result.append([i_elem['pos'], i_elem['tr'][0]['text']])
    return result
