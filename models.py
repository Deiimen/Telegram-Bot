import datetime
from peewee import IntegerField, CharField, BooleanField, DateField, AutoField, ForeignKeyField, Model, SqliteDatabase
from config import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """ Первоначальная инициализация БД"""
    class Meta:
        database = db


class User(BaseModel):
    """ Класс инициализации таблицы User с колонками перечисленными как атрибуты класса
        для сбора информации о пользователях
    """
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_name = CharField(null=True)


class Task(BaseModel):
    """ Класс инициализации таблицы Task с колонками перечисленными как атрибуты класса
        для сбора информации о задачах пользователей
    """
    task_id = AutoField()
    user_id = ForeignKeyField(User, backref='tasks')
    title = CharField()
    due_date = DateField()
    is_done = BooleanField(default=False)

    def __str__(self):
        """ Переопределение метода для вывода строки с 4-мя атрибутами в одну строку"""
        return '{id_task}. {done} {title} - {date}'.format(
            done='[V]' if self.is_done else '[ ]',
            id_task=self.task_id,
            title=self.title,
            date=self.due_date
        )


class History(BaseModel):
    """ Класс инициализации таблицы History с колонками перечисленными как атрибуты класса
        для сбора информации о переведенных словах, дате поиска по каждому пользователю
    """
    id_history = AutoField()
    user_id = ForeignKeyField(User, backref='history')
    word = CharField()
    date_add = DateField(default=datetime.datetime.today())


def create_model():
    """ Запуск создания таблиц (если не было)"""
    db.create_tables(BaseModel.__subclasses__())
