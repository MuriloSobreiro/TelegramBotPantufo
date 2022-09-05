import telebot
import os
from sqlmodel import Session, SQLModel, create_engine
from dotenv import load_dotenv
load_dotenv()

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class TelegramBot(metaclass=SingletonMeta):
    bot = telebot.TeleBot(os.environ["BOT_AUTH"])

class DataBase(metaclass=SingletonMeta):
    engine = create_engine(os.environ["DB"], connect_args={'check_same_thread': False})
    session = Session(engine, autoflush=False)