# Lab-4

## Usage

Just use `docker compose build` and `docker compose up`. You can see that whether the answer is from cache or not by looking at logs.

## Technologies

Web-part (probably incorrectly called `front` everywhere): python + flask
Worker: python
Cache: redis
Queue: redis
Database: sqlite

uuids are generated for books before written to queue.

## Examples of usage

### Create a book

Request:

`curl -d '{"name":"Illiad", "author": "Homer"}' -X POST 127.0.0.1:8000/save-book -H "Content-Type: application/json"`

Response:

`{"name": "Illiad", "author": "Homer", "uuid": "b40ed548-1c62-4e0f-8968-f1ef3f18a494"}`

### Get a book

Request:

`curl 127.0.0.1:8000/get-book/b40ed548-1c62-4e0f-8968-f1ef3f18a494`

Response:

`{"uuid": "b40ed548-1c62-4e0f-8968-f1ef3f18a494", "name": "Illiad", "author": "Homer"}`