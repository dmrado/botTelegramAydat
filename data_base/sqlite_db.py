import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('aydat_telegram_bot.db')
    cur = base.cursor()
    if base:
        print('Database is connected, successful!')
        base.execute('CREATE TABLE IF NOT EXISTS menu(id NUM PRIMARY KEY, name TEXT, email TEXT, flat TEXT)')
        base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()