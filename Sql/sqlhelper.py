#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import Queue
from threading import Thread
from time import sleep
from uuid import uuid4

import sqlite3


def is_sql_select(sql):
    return sql.lower().strip().startswith('select')


class SqlHelper(Thread):
    """
    A thread-safe sqlite worker

    Inspired by https://github.com/palantir/sqlite3worker
    """

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.queue = Queue()
        self.results = {}
        self.exit = False
        self._exit_token = str(uuid4())
        self.conn = sqlite3.connect(self.db, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.start()
        self.running = True

    def run(self):
        for token, sql, args, many in iter(self.queue.get, None):
            if token != self._exit_token:
                self._query(token, sql, args, many)
                if self.queue.empty():
                    self.conn.commit()

            if self.exit and self.queue.empty():
                self.conn.commit()
                self.conn.close()
                self.running = False
                return

    def close(self):
        self.exit = True
        self.queue.put((self._exit_token, '', (), 1))
        while self.running:
            sleep(0.01)

    def _query(self, token, sql, args, many):
        if is_sql_select(sql):
            try:
                if many:
                    self.cursor.executemany(sql, args)
                else:
                    self.cursor.execute(sql, args)
                self.results[token] = self.cursor.fetchall()
            except sqlite3.Error as e:
                self.results[token] = (
                    'Query error: {}: {}: {}'.format(sql, args, e))
        else:
            try:
                if many:
                    self.cursor.executemany(sql, args)
                else:
                    self.cursor.execute(sql, args)
            except sqlite3.Error as e:
                print('Query error: {}: {}: {}'.format(sql, args, e))

    def _query_result(self, token):
        delay = 0.001
        while True:
            if token in self.results:
                return self.results.pop(token)
            sleep(delay)
            if delay < 8:
                delay += delay

    def execute(self, sql=None, args=None, many=False):
        if self.exit:
            print('Exit called, not running: {}: {}'.format(sql, args))
            return 'Exit called'
        sql = sql or ''
        args = args or ()
        token = str(uuid4())
        if is_sql_select(sql):
            self.queue.put((token, sql, args, many))
            return self._query_result(token)
        else:
            self.queue.put((token, sql, args, many))

    def executemany(self, sql=None, args=None):
        self.execute(sql, args, many=True)
