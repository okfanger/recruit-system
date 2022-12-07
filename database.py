import math

import pymysql
from dbutils.pooled_db import PooledDB, SharedDBConnection


class MysqlPool(object):

    def __init__(self):
        self.POOL = PooledDB(
            creator=pymysql,
            maxconnections=10,  # 连接池的最大连接数
            maxcached=10,
            maxshared=10,
            blocking=True,
            setsession=[],
            host='localhost',
            port=3306,
            user='root',
            password='root',
            database='recruit-system',
            charset='utf8',
        )

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def connect(self):
        conn = self.POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self, conn, cursor):
        cursor.close()
        conn.close()

    def fetch_all(self, sql, args):
        conn, cursor = self.connect()
        if args is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)
        record_list = cursor.fetchall()
        return record_list

    def pagination(self, result_set, page_size, current_page):
        start_pos = page_size * (current_page - 1)
        end_pos = start_pos + page_size
        total_record = len(result_set)
        total_page = math.ceil(total_record / page_size)
        prev_num = current_page - 1 if current_page - 1 > 0 else 1
        next_num = current_page + 1 if current_page + 1 < total_page else total_page
        return {
            "result": result_set[start_pos: end_pos],
            "page_size": page_size,
            "current_page": current_page,
            "total_record": total_record,
            "total_page": total_page,
            "prev_url": f'?page_size={page_size}&current_page={prev_num}',
            "next_url": f'?page_size={page_size}&current_page={next_num}',
        }

    def fetch_one(self, sql, args):
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        return result

    def insert(self, sql, args):
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row

    def delete(self, sql, args):
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row


