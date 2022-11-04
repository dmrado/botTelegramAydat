from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

products_cb = CallbackData('product', 'id', 'action')


def get_admin_keyboard() -> InlineKeyboardMarkup:
    button_load = KeyboardButton('Get userlist')
    button_delete = KeyboardButton('Delete user')
    # метод add размещает кнопки друг над другом
    button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load) \
        .add(button_delete)
    return button_case_admin


# todo sql_read привязать к Get userlist


def get_start_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Просмотрт продуктов', callback_data='get_all_prod')],
        [InlineKeyboardButton('Добавить новый', callback_data='add_new_prod')]
    ])
    return ikb

def get_cancel_kb()-> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('/cancel')]
    ], resize_keyboard=True)
    return kb