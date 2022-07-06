from aiogram import Bot, Dispatcher, executor, types
from handlers.callbacks import twetter_register_callbacks
from handlers.messages import twetter_register_commands
from handlers.insta_handler import insta_register
from os import environ

API_TOKEN = environ["API_TOKEN"]
Cli = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(Cli)

insta_register(dp)
twetter_register_callbacks(dp)
twetter_register_commands(dp)

executor.start_polling(dp, skip_updates=True)