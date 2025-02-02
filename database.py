import sqlite3
from contextlib import ContextDecorator


class Database(ContextDecorator):
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, userid INTEGER, iid INTEGER);"
        )
        self.conn.commit()

    def insert(self, userid, iid):
        try:
            self.cur.execute(
                "SELECT * FROM bookmarks WHERE userid=? AND iid=?",
                (userid, iid),
            )
            rows = self.cur.fetchall()
            if rows:
                print(f"Record already exists: {rows}")
                return False

            self.cur.execute(
                "INSERT INTO bookmarks (userid, iid) VALUES (?, ?)",
                (userid, iid),
            )
            self.conn.commit()
            print(f"Record inserted: userid={userid}, iid={iid}")
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def search(self, userid=""):
        try:
            self.cur.execute(
                "SELECT * FROM bookmarks WHERE userid=?",
                (userid,),
            )
            rows = self.cur.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def delete(self, iid, userid):
        try:
            self.cur.execute(
                "DELETE FROM bookmarks WHERE iid=? AND userid = ? ", (iid, userid)
            )
            self.conn.commit()
            print(f"Record deleted: userid={userid}, iid={iid}")
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def __del__(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.conn.close()
        return False
