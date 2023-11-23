from telebot import TeleBot, StateMemoryStorage
from telebot.custom_filters import StateFilter
from telebot.types import BotCommand
from config import BOT_TOKEN, DEFAULT_COMMANDS
from models import create_model, User, Task, History
from telebot.handler_backends import State, StatesGroup
from yandex_translator import yandex_translate
import datetime
from functions import contains_digits, contains_only_latin_chars


class UserState(StatesGroup):
    """ Класс для создания состояний для автомата состояний"""
    title_task = State()
    due_date = State()
    mark_done = State()
    translator_word = State()


state_storage = StateMemoryStorage()

bot = TeleBot(BOT_TOKEN, state_storage=state_storage)


@bot.message_handler(commands=['start'])
def start_bot(message):
    """ Самая первая команда при открытии бота.
        Если пользователь новый, то приветствуем его и добавляем его id в БД
    """
    user_id = message.from_user.id
    username = message.from_user.username

    if User.get_or_none(user_id == User.user_id) is None:
        User.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        bot.send_message(user_id, f'Добро пожаловать {username}')
    else:
        bot.send_message(user_id, f'С возвращением {username}')


@bot.message_handler(state='*', commands=['newtask'])
def add_new_task(message):
    """ Опция главного меню: добавления задач и срока пользователя """
    user_id = message.from_user.id
    bot.send_message(user_id, 'Введите название задачи')
    bot.set_state(user_id, UserState.title_task)
    with bot.retrieve_data(user_id) as data:
        data['new_task'] = {'user_id': user_id}


@bot.message_handler(state='*', commands=['today'])
def add_new_task(message):
    """ Опция главного меню: отображению пользователю его задач сроки которых наступают сегодня """
    user_id = message.from_user.id
    user = User.get_or_none(user_id == User.user_id)
    user_tasks_today = user.tasks.\
        where(Task.due_date == datetime.datetime.today()).\
        order_by(-Task.task_id)

    # если user_tasks_today не существует то задач на дату не нашлось
    if not user_tasks_today:
        bot.send_message(user_id, 'На сегодня задач нет')
        return
    bot.send_message(user_id, '\n'.join(map(str, reversed(user_tasks_today))))
    bot.send_message(user_id, 'Какую задачу вы бы хотели отметить')
    bot.set_state(user_id, UserState.mark_done)


@bot.message_handler(state='*', commands=['tasks'])
def add_tasks(message):
    """ Опция главного меню: отображению пользователю всех его задач """
    user_id = message.from_user.id
    user = User.get_or_none(user_id == User.user_id)
    user_tasks = user.tasks.order_by(-Task.due_date, -Task.task_id).limit(10)
    bot.send_message(user_id, '\n'.join(map(str, reversed(user_tasks))))
    bot.send_message(user_id, 'Какую задачу вы бы хотели отметить')
    bot.set_state(user_id, UserState.mark_done)


@bot.message_handler(state="*", commands=["translator"])
def handle_translator(message) -> None:
    """ Опция главного меню: перевод введенного слова при помощи API с англ. на рус. """
    bot.send_message(message.from_user.id, "Введите слово на английском языке")
    bot.set_state(message.from_user.id, UserState.translator_word)


@bot.message_handler(state=UserState.mark_done)
def marked_done(message):
    """ Состояние ввода строки от пользователя для изменения статуса задачи с проверкой введенной информации
     на предмет: является ли введенное сообщение числом и если числом, то есть ли такая задача у пользователя
     """
    user_id = message.from_user.id
    try:
        task = int(message.text)
    except ValueError:
        bot.send_message(user_id, 'Некорректный ввод.\nВедите номер задачи еще раз')
        return
    if Task.get_or_none(Task.task_id == task) is None:
        bot.send_message(message.from_user.id, "Задачи с таким ID не существует.")
        return
    user_task = Task.get_or_none(Task.task_id == task)
    user_task.is_done = not user_task.is_done
    user_task.save()

    bot.send_message(user_id, f'Задача {task} изменена\n {user_task}')
    bot.delete_state(user_id)


@bot.message_handler(state=UserState.title_task)
def add_date(message):
    """ Состояние ввода строки от пользователя для добавления в БД названия задачи пользователя """
    user_id = message.from_user.id
    bot.send_message(user_id, 'Введите дату задачи')
    bot.set_state(user_id, UserState.due_date)
    with bot.retrieve_data(user_id) as data:
        data['new_task']['title'] = message.text


@bot.message_handler(state=UserState.due_date)
def add_date(message):
    """ Состояние ввода строки от пользователя для добавления в БД срок задачи пользователя """
    user_id = message.from_user.id
    try:
        message.text == datetime.datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError:
        bot.send_message(user_id, 'Некорректный ввод.\nВедите дату в формате дд.мм.гггг')
        return
    bot.set_state(user_id, UserState.due_date)
    with bot.retrieve_data(user_id) as data:
        data['new_task']['due_date'] = datetime.datetime.strptime(message.text, '%d.%m.%Y')
    bot.send_message(user_id, 'Задача добавлена')
    bot.delete_state(user_id)
    Task.create(**data['new_task'])


@bot.message_handler(state=UserState.translator_word)
def translate(message) -> None:
    """ Состояние ввода строки от пользователя для поиска слова при помощи API """
    user_id = message.from_user.id
    if contains_digits(message.text):
        bot.send_message(user_id, 'Некорректный ввод.\nВведите слово без цифр')
        return
    if not contains_only_latin_chars(message.text):
        bot.send_message(user_id, 'Некорректный ввод.\nВводите символы только на латинице')
        return

    result = yandex_translate(message.text)
    bot.send_message(message.from_user.id, 'Перевод\n')
    History.create(user_id=message.from_user.id, word=message.text)

    # Выводим пользователю перевод слова сообщением в боте построчно
    for i_word in range(len(result)):
        ret = ''.join([result[i_word][0], ': ', result[i_word][1]])
        bot.send_message(message.from_user.id, ret.title())


if __name__ == '__main__':
    create_model()
    bot.add_custom_filter(StateFilter(bot))
    bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])
    bot.polling()
