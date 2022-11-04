import sqlite3 as sq
from main import bot

cur = None


def sql_start():
    global db, cur
    db = sq.connect('aydat_telegram_bot.db')
    cur = db.cursor()
    if db:
        print('Database is connected, successful!')
        db.execute('CREATE TABLE IF NOT EXISTS menu(name TEXT, email TEXT, flat TEXT)')
        db.commit()


# todo пофиксить cur.execute
async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?, ?)', tuple(data.values()))
        db.commit()


# get userList for admin request, where ret contains response from db
async def sql_read(message):
    for ret in cur.execute('SELECT * FROM menu').fetchall():
        await bot.send_user(message.from_user.id, ret[0], f'{ret[1]}\nName: {ret[2]}\nEmail: {ret[3]}\nFlat {ret[4]}')


async def get_all_prod():
    products = cur.execute("SELECT * FROM menu").fetchall()
    return products

async def create_new_product(title, prod_id):
    product = cur.execute("INSERT INTO menu VALUES (?, ?)", (title, prod_id))
    db.commit()
    return product
