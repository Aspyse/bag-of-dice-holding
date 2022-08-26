from tabnanny import check
import aiosqlite
import os
from rolling_implementation import cleanroll

db_file = 'database.db'
schema_file = 'schema.sql'

with open(schema_file, 'r') as rf:
        # Read the schema from the file
        schema = rf.read()

async def storedice(user, name, notation, emoji=""):
    await check_db()
    notation = await cleanroll(notation)

    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM dice WHERE user=?", (user,))
    if len(await cursor.fetchall()) < 25:
        await conn.execute("INSERT INTO dice VALUES (?, ?, ?, ?)", (user, name, notation, emoji))
        await conn.commit()
        await conn.close()
        # return (name, notation, emoji)
    else:
        await conn.close()
        raise Exception() # LMFAO WHAT AM I DOING

async def deletealldice(user):
    await check_db()
    conn = await aiosqlite.connect(db_file)
    await conn.execute("DELETE FROM dice WHERE user=?", (user,))
    await conn.commit()
    await conn.close()

async def getdice(user):
    await check_db()
    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM dice WHERE user=?", (user,))
    rows = await cursor.fetchall()
    await conn.close()
    return rows

async def removedice(user, alias):
    await check_db()
    conn = await aiosqlite.connect(db_file)
    await conn.execute("DELETE FROM dice WHERE user=? AND alias=?", (user, alias))
    await conn.commit()
    await conn.close()

async def updatedice(user, alias1, alias2, notation, emoji=""):
    await check_db()
    notation = await cleanroll(notation)
    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    #await cursor.execute("SELECT * FROM dice WHERE user=? AND alias=?", (user, alias2))
    if alias1 == alias2 or len(await cursor.fetchall()) < 1:
        await conn.execute("UPDATE dice SET alias=?, command=?, emoji=? WHERE user=? AND alias=?", (alias2, notation, emoji, user, alias1))
        await conn.commit()
    await conn.close()

async def check_db():
    if not os.path.exists(db_file):
        conn = await aiosqlite.connect(db_file)
        await conn.executescript(schema)