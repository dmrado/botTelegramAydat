# admin keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_load = KeyboardButton('Get userlist')
button_delete = KeyboardButton('Delete user')
# метод add размещает кнопки друг над другом
button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
    .add(button_delete)
# todo sql_read приявязать к Get userlist