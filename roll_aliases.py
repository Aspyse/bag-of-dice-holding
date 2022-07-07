import aiosqlite
import os
from rolling_implementation import cleanroll

db_file = 'database.db'
schema_file = 'schema.sql'

with open(schema_file, 'r') as rf:
        # Read the schema from the file
        schema = rf.read()

async def savedice(user, name, notation):
    notation = cleanroll(notation)

    if not check_db(db_file):
        async with aiosqlite.connect(db_file) as conn:         
            # Execute the SQL query to create the table
            await conn.executescript(schema)
            print('Created the Table! Now inserting')

    conn = await aiosqlite.connect(db_file)
    await conn.execute("INSERT INTO dice VALUES (?, ?, ?)", (user, name, notation))
    print('Inserted values into the table!')
    await conn.close()
    print('Closed the connection!')

    return (name, notation)

async def getdice(user):
    conn = await aiosqlite.connect(db_file)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM dice WHERE user=?", (user,))
    rows = await cursor.fetchall()
    loop.create_task(conn.close())
    return rows

def check_db(filename):
    return os.path.exists(filename)