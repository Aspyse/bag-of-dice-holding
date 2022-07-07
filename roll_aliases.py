import sqlite3
#import os
from rolling_implementation import cleanroll

def savedice(command, user, guild):
    command = command.split(' ')
    name = command[0]
    roll = cleanroll(command[1])
    

    db_file = f'{guild}{user}.db'
    schema_file = 'schema.sql'
    
    with open(schema_file, 'r') as rf:
        # Read the schema from the file
        schema = rf.read()

    if not check_db(db_file):
        with sqlite3.connect(db_file) as conn:         
            # Execute the SQL query to create the table
            conn.executescript(schema)
            print('Created the Table! Now inserting')

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dice VALUES (?, ?, ?)", (user, name, roll))
#        conn.executescript("""
#                        insert into dice (alias, command)
#                        values ({0}, {1})
#                        """.format(name, roll))
        print('Inserted values into the table!')
    print('Closed the connection!')

    return f"alias created {name} -> {roll} in {guild}"

#def check_db(filename):
#    return os.path.exists(filename)