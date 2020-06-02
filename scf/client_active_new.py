# -*- coding: utf8 -*-
import datetime
import pymysql.cursors
import logging
import sys
import pytz
import json, hashlib, time
import base64
#
# MySql数据库账号信息,需要提前创建好数据库
Host = 'IP'
User = 'USER'
Password = 'PASSWORD'
Port = 00000 # port
DB = u'db'

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

g_connection = None
g_connection_errinfo = None
def connect_mysql():
    global g_connection
    global g_connection_errinfo
    try:
        g_connection = pymysql.connect(host=Host,
                                     user=User,
                                     password=Password,
                                     port=Port,
                                     db=DB,
                                     charset='utf8',
                                     autocommit = True,
                                     cursorclass=pymysql.cursors.DictCursor)
        return True, []
    except Exception as e:
        g_connection = None
        g_connection_errinfo = e;
        return False, e

print("connect database")
connect_mysql()

def recheck_connect():
    global g_connection
    if not g_connection:
        rflag, errorinfo = connect_mysql()
        if not rflag:
            return False, json.dumps(errorinfo)
    with g_connection.cursor() as cursor:
        try:
            sql = 'show databases'
            cursor.execute(sql)
            res = cursor.fetchall()
        except Exception as e:
            rflag, errorinfo = connect_mysql()
            if not rflag:
                return False, json.dumps(errorinfo)
    cursor.close()
    return True, res

def sql_read( sql):
    global g_connection
    with g_connection.cursor() as cursor:
        try:
            cursor.execute(sql)
            return True, cursor.fetchall()
        except Exception as e:
            return False, "write failed : %s"%e

def main_handler(event, context):
    # base test
    stime = time.time()
    ctime = stime

    # offline reset
    sql = 'update client set astatus = 0 where activetime < date_sub(now(),interval 120 MINUTE_SECOND)'
    rflag, rdata = sql_read(sql)
    if not rflag:
        print rdata
        return False
    ctime = time.time()
    print 'ut:'+str(ctime-stime)
    stime = ctime
    
    # online update
    sql = 'update client t2, \
(select clientid, max(time) as time, PM1, PM2d5, PM10 from base_data where time > date_sub(now(),interval 120 MINUTE_SECOND) group by clientid)  t1 \
set t2.activetime = t1.time, t2.astatus = 1, t2.PM1 = t1.PM1, t2.PM2d5 = t1.PM2d5, t2.PM10 = t1.PM10 \
where t1.clientid = t2.uid'

    rflag, rdata = sql_read(sql)
    if not rflag:
        print rdata
        return False
    ctime = time.time()
    print 'ut:'+str(ctime-stime)
    stime = ctime
    return True

