import json
import redis
import os
import sqlite3

WRITE_ID = "1"
READ_ID = "2"


def save_book(book):
    uuid = book["uuid"]
    name = book["name"]
    author = book["author"]
    cur.execute("INSERT INTO BOOKS (uuid, name, author) VALUES ('%s', '%s', '%s')" % (
        uuid, name, author))
    sqlite_conn.commit()


def get_book(uuid):
    cur.execute("SELECT uuid, name, author FROM books WHERE uuid = '%s'" % uuid)
    data = cur.fetchall()
    book = ""
    if not data:
        print('Book not found. Writing negative response to cache')
    else:
        print('Book found. Putting to cache')
        book = json.dumps({
            "uuid": data[0][0],
            "name": data[0][1],
            "author": data[0][2],
        })
    rds.set(uuid, book, ex = 5)
    rds.xadd(WRITE_ID, {"type": "get_book", "book": book})


def create_sqlite_conn():
    sqlite_conn = sqlite3.connect("/db/db.sqlite")
    cur = sqlite_conn.cursor()
    cur.execute(
        '''
    CREATE TABLE IF NOT EXISTS books (
        uuid TEXT PPIMARY KEY,
    	name TEXT NOT NULL,
    	author TEXT NOT NULL
    );
    ''')
    sqlite_conn.commit()
    return (cur, sqlite_conn)


def read_event():
    global last_id
    events = rds.xread({READ_ID: last_id}, block=300_000, count=1)
    if len(events) == 0:
        return None

    response = events[0][1]
    
    event_id = response[0][0]
    event_obj = response[0][1]
    last_id = event_id
    return event_obj

def process_event(event):
    if not event:
        return
    elif event["type"] == "save_book":
        print("Request to save book")
        save_book(json.loads(event["book"]))
    elif event["type"] == "get_book":
        print("Request to get book")
        get_book(event["uuid"])


if __name__ == '__main__':
    print("Worker starts")

    # Initialize Redis connection
    rds = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=os.getenv("REDIS_PORT", "6379"),
        password=os.getenv("REDIS_PASSWORD", ""),
        decode_responses=True
    )
    print("Connected to Redis")

    (cur, sqlite_conn) = create_sqlite_conn()

    print("Connected to Sqlite")

    last_id = "$"
    while True:
        process_event(read_event())
