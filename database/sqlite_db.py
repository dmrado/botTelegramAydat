import sqlite3 as sq
from main import bot
cur = None

def sql_start():
    global base, cur
    base = sq.connect('aydat_telegram_bot.db')
    cur = base.cursor()
    if base:
        print('Database is connected, successful!')
        base.execute('CREATE TABLE IF NOT EXISTS menu(id NUM PRIMARY KEY, name TEXT, email TEXT, flat TEXT)')
        base.commit()

# todo пофиксить cur.execute
async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


# get userList for admin request, where ret contains response from db
async def sql_read(message):
    for ret in cur.execute('SELECT * FROM menu').fetchall():
        await bot.send_user(message.from_user.id, ret[0], f'{ret[1]}\nName: {ret[2]}\nEmail: {ret[3]}\nFlat {ret[4]}')
