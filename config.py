import os
from dotenv import load_dotenv, find_dotenv

""" Первоначальная инициация констант, загрузка данных из переменной среды разработки"""

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

DB_PATH = "C:\sqlite\database2.db"
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
BASE_URL = 'https://dictionary.yandex.net/api/v1/dicservice.json'

DEFAULT_COMMANDS = (
    ("newtask", "Создать задачу"),
    ("tasks", "Последние 10 задач"),
    ("today", "Задачи на сегодня"),
    ("translator", "Переводчик")
)

DATE_FORMAT = "%d.%m.%Y"