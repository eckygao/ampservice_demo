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

def sql_exec( sql, sqldata):
    global g_connection
    try:
        with g_connection.cursor() as cursor:
            cursor.executemany(sql, sqldata)
            g_connection.commit()
        return True, None
    except Exception as e:
        g_connection.rollback()
        return False, "write failed : %s"%e

def getlevel( data):
    if data < 50:
        return 1
    if data < 100:
        return 2
    if data < 150:
        return 3
    if data < 200:
        return 4
    if data < 300:
        return 5
    return 6

def main_handler(event, context):
    # base test
    clientlist = { 'isBase64Encoded': False,'statusCode': 200,'headers': {},'body': []}
    print event
    #
    keytype = 'all'
    if 'type' not in event['queryString'].keys():
        keytype = 'all'
    elif event['queryString']['type'] not in ['all','active']:
        return clientlist
    else:
        keytype = event['queryString']['type']

    print keytype
    if 'all' == keytype:
        sql = 'select * from client order by devicename asc '
    else:
        sql = 'select * from client where astatus = 1 order by devicename asc '

    rflag, rdata = sql_read(sql)
    if not rflag:
        print rdata
        return clientlist
    tmpinfo = [];
    for i in rdata:
        tmp = {'dname':i['devicename'],
        'clientid':i['uid'],
        'lat':float(i['latitude']),
        'lng':float(i['longitude']),
        'uptime':str(i['activetime']),
        'astatus':'在线'if 1 == i['astatus'] else '',
        'PM1':i['PM1'],
        'PM2d5':i['PM2d5'],
        'PM10':i['PM10'],
        'status':str(getlevel(i['PM2d5']) )
        }
        tmpinfo.append(tmp);
    clientlist['body'] = json.dumps(tmpinfo);
    
    return clientlist

