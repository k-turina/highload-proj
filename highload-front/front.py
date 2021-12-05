from collections import defaultdict
import json
import redis
import os
import uuid
from flask import Flask, Response, request

WRITE_ID = "2"
READ_ID = "1"
last_id = "$"


app = Flask(__name__)

rds = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=os.getenv("REDIS_PORT", "6379"),
    password=os.getenv("REDIS_PASSWORD", ""),
    decode_responses=True
)


@app.route("/save-book", methods=["POST"])
def create_book() -> Response:
    book = request.json
    if not isinstance(book, dict) or {"name", "author"} - set(book.keys()):
        return Response("Invalid data", status=400)
    book["uuid"] = str(uuid.uuid4())
    rds.xadd(WRITE_ID, {"book": json.dumps(book), "type": "save_book"})
    return Response(json.dumps(book), mimetype="application/json")


def read_event():
    global last_id
    events = rds.xread({READ_ID: last_id}, block=500_000, count=1)[0][1]
    last_id = events[0][0]
    return events[0][1]


def get_book_through_cache(uuid):
    print("Trying to get book with uuid %s" % uuid, flush=True) 
    value = rds.get(uuid)

    if not value:
        print('Not found in cache', flush=True)
        rds.xadd(WRITE_ID, {"type": "get_book", "uuid": uuid})
        return read_event()["book"]


    print("Found in cache", flush=True)
    return value


@app.route("/get-book/<uuid>", methods=["GET"])
def get_book(uuid: int) -> Response:
    book = get_book_through_cache(uuid)
    if book:
        return Response(book, mimetype="application/json")
    else: 
        return Response('{"error": "Not Found"}', mimetype="application/json", status=404) 


app.run(host="0.0.0.0", port=8000, debug=True)
print("Web STARTED")
