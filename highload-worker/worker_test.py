import unittest
import worker

class WorkerTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
        worker.create_sqlite_conn(":memory:")


    def setUp(self) -> None:
        pass

    def test_book_is_added(self):
        uuid = "Test UUID"
        name = "Test Book"
        author = "Test Author"
        book = {
            "uuid": uuid,
            "name": name,
            "author": author,
        }
        worker.save_book(book)
        worker.cur.execute("SELECT uuid, name, author FROM books WHERE uuid = '%s' AND name = '%s' AND author = '%s'" % (uuid, name, author))
        data = worker.cur.fetchall()
        self.assertTrue(data, "Written book can be found in a database")

    def test_wrong_test(self):
        uuid = "Test UUID"
        name = "Test Book"
        author = "Test Author"
        book = {
            "uuid": uuid,
            "name": name,
            "author": author,
        }
        worker.save_book(book)
        worker.cur.execute("SELECT * FROM books")
        data = worker.cur.fetchall()
        self.assertTrue(data, "There should be at least one book now")

    def tearDown(self) -> None:
        worker.cur.execute("DELETE FROM books")
        worker.sqlite_conn.commit()
        pass

if __name__ == '__main__':
    unittest.main()
