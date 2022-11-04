# пример
# @bot.callback_query_handler(func=lambda call: True)
# def ans(call):
#     if call.data == 'ZHALOBA':
#         func1(call.message, call)

# def func1(message, call):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(*[types.KeyboardButton(name) for name in ['Назад']])
#     bot.send_message(message.chat.id, "Отправьте мне текст для жалобы", reply_markup=keyboard)
# @bot.message_handler(content_types=['text'])
# def test(message):
#     if message.text == 'Назад':
#         start(message)

#     elif message.text != None:
#         zhaloba = message.text


# пример
# @dp.message_handler()
# async def echo(message: types.Message):

#     markup = InlineKeyboardMarkup().add(
#         InlineKeyboardButton("Кнопка1", callback_data="but_1"),
#         InlineKeyboardButton("Кнопка2", callback_data="but_2"),
#         InlineKeyboardButton("JBT", callback_data="jbt"),
#     )

#     await message.answer(message.text, reply_markup=markup)
#     logging.info(f"{message.from_user.username}: {message.text}")
