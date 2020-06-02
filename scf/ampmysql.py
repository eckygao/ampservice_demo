# -*- coding: utf8 -*-
import pymysql.cursors
import json

class AmpMysql(object):
    """docstring for AmpMysql"""
    def __init__(self, host, user, password, port, db):
        self._errorinfo = ''
        self._db_host = host;
        self._db_user = user;
        self._db_passwd = password;
        self._db_port = port;
        self._db_db   = db;

    def get_errorinfo(self):
        return self._errorinfo;

    def connect(self):
        try:
            self._connection = pymysql.connect(
                host = self._db_host,
                user = self._db_user,
                password = self._db_passwd,
                port = self._db_port,
                db   = self._db_db,
                charset ='utf8',
                autocommit = True,
                cursorclass=pymysql.cursors.DictCursor)
            return True
        except Exception as e:
            self._connection = None
            self._errorinfo = e
            return False

    def check_connect(self):
        # check and connect
        if not self._connection:
            if not self.connect():
                return False
        # test
        with self._connection.cursor() as cursor:
            try:
                sql = 'show databases'
                cursor.execute(sql)
                res = cursor.fetchall()
            except Exception as e:
                if not self.connect():
                    return False
        return True

    def sql_read( self, sql):
        with self._connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                return True, cursor.fetchall()
            except Exception as e:
                return False, "write failed : %s"%e

    def sql_exec( self, sql, sqldata):
        try:
            with self._connection.cursor() as cursor:
                cursor.executemany(sql, sqldata)
                self._connection.commit()
            return True
        except Exception as e:
            self._connection.rollback()
            self._errorinfo = "write failed : %s"%e
            return False
