import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
import admin_keybord

from settings_local import API_TOKEN

logging.basicConfig(level=logging.DEBUG)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# start database
# sqlite_db.sql_start()

# for admin
ID = None

# create states
class FSMAdmin(StatesGroup):
    name = State()
    email = State()
    flat = State()
    # photo = State()

# ID of a current admin
@dp.message_handler(commands=['admin'])
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, "What do you want?", reply_markup=admin_keybord.button_case_admin)

    await message.delete()


# todo <if message.from_user.id == ID> add to admit`s requests first command of the def

# start of the dialogue
@dp.message_handler(commands="register", state=None)
# pass to FSM-regime
async def cm_start(message: types.Message):
    await FSMAdmin.name.set()
    await message.reply('Input you name, please')

# catch first answer from a user
@dp.message_handler(content_types =['text'], state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    # save the name into dictionary (state.proxy() as data) of state machines
    async with state.proxy() as data:
        # data is a dict and has own methods
        data['name'] = message.text
        await FSMAdmin.next()
        await message.reply("Then input your email, please/ введите email")


@dp.message_handler(content_types=['text'], state=FSMAdmin.email)
async def load_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        # todo сообщение о некорректности введенных даных
        await FSMAdmin.next()
        await message.reply("Then input your flat, please/ введите квартиру")
        # todo валидация email


@dp.message_handler(content_types=['text'], state=FSMAdmin.flat)
async def load_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['flat'] = message.text
        # todo валидация flat

    await sqlite_db.sql_add_command(state)

    async with state.proxy() as data:
        await message.reply(str(data))


    await state.finish()

# abort from any
@dp.message_handler(state="*", commands='abort')
@dp.message_handler(Text(equals='(^(отмена|abort)?)', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Ok!")


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

    markup = ReplyKeyboardMarkup().add(
        KeyboardButton("ГЛАВНАЯ КНОПКА")
    )

    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram and by Dmitrii little.", reply_markup=markup)
    await message.answer(f"Your id is {message.from_user.id}")

    logging.info(f"{message.from_user.username}: {message.text}")


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    await message.reply(text='Cats are here 😺')
    logging.info(f"{message.from_user.username}: {message.text}")


# @dp.message_handler()
# async def echo(message: types.Message):
#
#     markup = InlineKeyboardMarkup().add(
#         InlineKeyboardButton("Кнопка1", callback_data="but_1"),
#         InlineKeyboardButton("Кнопка2", callback_data="but_2"),
#         InlineKeyboardButton("JBT", callback_data="jbt"),
#     )
#
#     await message.answer(message.text, reply_markup=markup)
#     logging.info(f"{message.from_user.username}: {message.text}")


@dp.callback_query_handler(text_startswith="but_")
async def but_pressed(call: types.CallbackQuery):
    logging.info(f"{call.from_user.username}: {call.data}")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("ГЛАВНАЯ КНОПКА"),
    )
    markup.row(
        KeyboardButton("Кнопка3", request_location=True),
    )
    markup.insert("Кнопка4")

    await call.message.answer(text=f"You pressed {call.data}", reply_markup=markup)
    await call.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)