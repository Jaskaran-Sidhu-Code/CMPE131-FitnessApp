import sqlite3
from js import console

conn = sqlite3.connect('database.db')

def create(*args, **kwargs):
    conn.execute('''CREATE TABLE items
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    item_name          TEXT        NOT NULL,
    quantity           INT         NOT NULL)''')
    console.log("Table created")

def insert(*args, **kwargs):
    conn.execute("INSERT INTO items(item_name, quantity) VALUES('Apple', 5)")
    console.log("Item inserted")

def fetch(*args, **kwargs):
    cursor = conn.execute(*SELECT id, item_name, quantity FROM items*)
    for row in cursor:
        console.log(row[0], row[1], row[2])