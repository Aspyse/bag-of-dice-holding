import aiosqlite
import os
from rolling_implementation import cleanroll

db_file = 'database.db'
schema_file = 'schema.sql'

with open(schema_file, 'r') as rf:
        # Read the schema from the file
        schema = rf.read()

async def storedice(user, name, notation):
    notation = await cleanroll(notation)

    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM dice WHERE user=?", (user,))
    if len(await cursor.fetchall()) < 25:
        await conn.execute("INSERT INTO dice VALUES (?, ?, ?)", (user, str(name), notation))
        await conn.commit()
        await conn.close()
        return (name, notation)
    await conn.close()

async def deletealldice(user):
    conn = await aiosqlite.connect(db_file)
    await conn.execute("DELETE FROM dice WHERE user=?", (user,))
    await conn.commit()
    await conn.close()

async def getdice(user):
    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM dice WHERE user=?", (user,))
    rows = await cursor.fetchall()
    await conn.close()
    return rows

async def removedice(user, alias):
    conn = await aiosqlite.connect(db_file)
    await conn.execute("DELETE FROM dice WHERE user=? AND alias=?", (user, alias))
    await conn.commit()
    await conn.close()

async def updatedice(user, alias1, alias2, notation):
    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM dice WHERE user=? AND alias=?", (user, alias2))
    if alias1 == alias2 or len(await cursor.fetchall()) < 1:
        await conn.execute("UPDATE dice SET alias=?, command=? WHERE user=? AND alias=?", (alias2, notation, user, alias1))
        await conn.commit()
    await conn.close()

async def check_db():
    if not os.path.exists(db_file):
        conn = await aiosqlite.connect(db_file)
        await conn.executescript(schema)
    return 