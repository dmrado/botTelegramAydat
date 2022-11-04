import logging
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from database import sqlite_db
from keyboards import get_admin_keyboard, get_start_ikb, products_cb, get_cancel_kb

from settings_local import API_TOKEN

logging.basicConfig(level=logging.DEBUG)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


# start database
async def on_startup(_):
    await sqlite_db.sql_start()


# for admin
ID = None


# остановка процесса, вызовем где надо
@dp.message_handler(commands=['cancel'], state="*")
# @dp.message_handler(Text(equals='(^(отмена|abort|cancel)?)', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await state.finish()
    await message.reply("Canceled successful!")
    return


# ID текущего администратора
@dp.message_handler(commands=['admin'])
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(ID, "What`s your wish?")
    # markup = get_admin_keyboard
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Get userlist", callback_data='get_list'),
        InlineKeyboardButton("Delete user", callback_data='del_user'),
        # InlineKeyboardButton("JBT", callback_data="jbt"),
    )
    await message.answer(message.text, reply_markup=markup)
    logging.info(f"{message.from_user.username}: {message.text}")

    await message.delete()


# todo определить что это делает и доделать
@dp.callback_query_handler(text_startswith="but_")
async def admin_button_pressed(call: types.CallbackQuery):
    logging.info(f"{call.from_user.username}: {call.data}")
    if (call.data == "get_list"):
        await message.answer(message.text, "Get userlist is pushed")
    elif (call.data == "del_user"):
        await message.answer(message.text, "Delete user is pushed")
    # else:
    #   await message.answer(message.text, "Nothing selected")

    await call.message.answer


# todo <if message.from_user.id == ID> add to admit`s requests by the first command of the def

# создаем стейты для команды register
class FSMAdmin(StatesGroup):
    name = State()
    email = State()
    flat = State()
    # photo = State()

# создаем стейты для сохранения чека
class Prod(StatesGroup):
    title = State()
    photo = State()


# start диалога для работы стейт-машины для FSMAdmin, команда register
@dp.message_handler(commands="register", state=None)
# pass to FSM-regime by the set()-command Запускаем стейт-машину
async def cm_start(message: types.Message):
    await FSMAdmin.name.set()
    await message.reply('Input your name, please')


# отлавливаем первый ответ user
@dp.message_handler(content_types=['text'], state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    # сохраняем name в dictionary (state.proxy() as data) в стейте FSMAdmin
    async with state.proxy() as data:
        # data - это словарь в который мы складываем все значения
        data['name'] = message.text
        await FSMAdmin.next()
        await message.reply("Then input your email, please/ введите email")


@dp.message_handler(content_types=['text'], state=FSMAdmin.email)
async def load_email(message: types.Message, state: FSMContext):
    if (re.fullmatch("[\d\w\-\.]+@[\d\w\-\.]+.[\d\w\-\.]+", message.text)):
        async with state.proxy() as data:
            data['email'] = message.text
            await FSMAdmin.next()
            await message.reply("And now input your flat, please/ введите номер квартирЫ")
    else:
        await message.reply("email is incorrect")


@dp.message_handler(content_types=['text'], state=FSMAdmin.flat)
async def load_flat(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['flat'] = message.text
        # todo валидация flat возможн и не нужна, а может сделать сверку со списком жильцов

    await sqlite_db.sql_add_new_user(state)

    async with state.proxy() as data:
        await message.reply(str(data))
    # Останавливаем стейт-машину очищаем стейт
    await state.finish()


# обрабатываем команду start, по этой команде предлагаем просмотреть или внести чек
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Hi!", reply_markup=get_start_ikb())
    # await message.answer(f"Your id is {message.from_user.id} and your name is {message.from_user.name}")
    logging.info(f"{message.from_user.username}: {message.text}")


# Обрабатываем keyboards/get_start_ikb, по callback_query=get_all_prod
@dp.callback_query_handler(text='get_all_prod')
async def get_all_prod(callback: types.CallbackQuery):
    products = await sqlite_db.get_all_prod()
    if not products:
        await callback.message.delete()
        await callback.message.answer('Продуктов нет')
        return await callback.answer()

    await callback.message.answer(products)
    # что-бы не появлялся тайминг на инлайн-кнопке
    await callback.answer()


# Обрабатываем keyboards/add_new_prod, по callback_query=add_new_prod
@dp.callback_query_handler(text='add_new_prod')
async def create_new_prod(callback: types.CallbackQuery) -> None:
    await callback.message.delete()
    # старт стейт-машины для Prod
    await Prod.title.set()
    await callback.message.answer("Send name of prod/Отправьте название продукта", reply_markup=get_cancel_kb())


@dp.message_handler(content_types=['text'], state=Prod.title)
async def load_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

        await Prod.next()
        await message.reply("Send photo of a bill/Отправьте фото чека")


# обрабатываем если user отправил не фото
@dp.message_handler(lambda message: not message.photo)
async def check_photo(message: types.Message):
    await message.reply('Not photo/Это не фото!')


# обрабатываем правильное фото
@dp.message_handler(content_types=['photo'], state=Prod.photo)
async def load_photo(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await sqlite_db.create_new_product(state)
    await message.reply('Great! Your bill was stored/Чек сохранен', reply_markup=get_start_ikb())

    await state.finish()


# если user заказал котиков он их получает
@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    await message.reply(text='Cats are here 😺')
    logging.info(f"{message.from_user.username}: {message.text}")


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