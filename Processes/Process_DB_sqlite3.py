from Processes import Process

import asyncio
import sqlite3
import pathlib

class DBSQLite3(Process.SingleProcess):
    def __init__(self, event_loop):
        super(DBSQLite3, self).__init__()

        self.loop = event_loop

        sqlite_file = '/Users/Sebastian/Desktop/my_db.sqlite'
        self.connection = sqlite3.connect(sqlite_file)
        self.cursor = self.connection.cursor()

    async def write(self):
        pass

    async def

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    db = DBSQLite3(loop)
