import sqlite3
from contextlib import ContextDecorator

from bot.config import logger


class Database(ContextDecorator):

    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, userid INTEGER, iid INTEGER);"
        )

        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY, userid INTEGER, page INTEGER);"
        )
        self.conn.commit()

    def insert_bookmark(self, userid, iid):
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
            logger.info("Record inserted: userid=%s, iid=%s", userid, iid)
            return True
        except sqlite3.Error as e:
            logger.error(
                "Database error: %s - insert_bookmark: userid=%s, iid=%s",
                e,
                userid,
                iid,
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error: {e} - insert_bookmark: userid={userid}, iid={iid}"
            )
            return False

    def search_bookmark(self, userid=""):
        try:
            self.cur.execute(
                "SELECT * FROM bookmarks WHERE userid=?",
                (userid,),
            )
            rows = self.cur.fetchall()
            logger.info(f"Record found: userid={userid}, rows={rows}")
            return rows
        except sqlite3.Error as e:
            logger.error(f"Database error: {e} - search_bookmark: userid={userid}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e} - search_bookmark: userid={userid}")
            return []

    def delete_bookmark(self, iid, userid):
        try:
            self.cur.execute(
                "DELETE FROM bookmarks WHERE iid=? AND userid = ? ", (iid, userid)
            )
            self.conn.commit()
            logger.info(f"Record deleted: userid={userid}, iid={iid}")
            return True
        except sqlite3.Error as e:
            logger.error(
                f"Database error: {e} - delete_bookmark: userid={userid}, iid={iid}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error: {e} - delete_bookmark: userid={userid}, iid={iid}"
            )
            return False

    def search_page(self, userid):
        try:
            self.cur.execute(
                "SELECT * FROM pages WHERE userid=?",
                (userid,),
            )
            rows = self.cur.fetchall()
            return rows
        except sqlite3.Error as e:
            logger.error(f"Database error: {e} - search_page: userid={userid}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e} - search_page: userid={userid}")
            return []

    def upsert_page(self, userid, page):
        try:
            self.cur.execute(
                "SELECT * FROM pages WHERE userid=?",
                (userid,),
            )
            rows = self.cur.fetchall()
            if rows:
                self.cur.execute(
                    "UPDATE pages SET page=? WHERE userid=?",
                    (page, userid),
                )
                self.conn.commit()
                logger.info(f"Record updated: userid={userid}, page={page}")
                return True

            self.cur.execute(
                "INSERT INTO pages (userid, page) VALUES (?, ?)",
                (userid, page),
            )
            self.conn.commit()
            logger.info(f"Record inserted: userid={userid}, page={page}")
            return True
        except sqlite3.Error as e:
            logger.error(
                f"Database error: {e} - upsert_page: userid={userid}, page={page}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error: {e} - upsert_page: userid={userid}, page={page}"
            )
            return False

    def __del__(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.conn.close()
        return False
