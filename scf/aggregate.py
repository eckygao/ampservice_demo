# -*- coding: utf8 -*-
import datetime
import pymysql.cursors
import logging
import sys
import pytz
import json, hashlib, time
import base64
#

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

def get_clientid( typeid, stime, etime):
    # set param
    if 'hour' ==  typeid:
        sql_dname = 'select distinct(clientid) as dname from base_data \
            where time >= from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") \
                and time < from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s")'
    elif 'day' == typeid:
        sql_dname = 'select distinct(clientid) as dname from aggregate_data \
            where starttime >= from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") \
                and starttime < from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s")'
    else:
        return False, 'Unknown type : %s'%typeid
    # get device
    rflag, dndata = sql_read( sql_dname%(stime, etime))
    if not rflag:
        return False, dndata
    rdata = []
    for i in dndata:
        rdata.append(i['dname'])
    return True, rdata

def get_avg_s2e( typeid, dname, stime, etime):
    # set param
    if 'hour' ==  typeid:
        sql_getdata = 'select pm1, pm2d5, pm10 from base_data where \
            time >= from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") \
                and time < from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") \
                    and clientid = "%s"'
    elif 'day' == typeid:
        sql_getdata = 'select updatecount, pm1, pm2d5, pm10 from aggregate_data where \
            starttime >= from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") \
                and starttime < from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") \
                    and clientid = "%s" and utype = 3'
    else:
        return False, 'Unknown type : %s'%typeid
    # get data
    rflag, rdata = sql_read( sql_getdata%(stime, etime,dname))
    if not rflag:
        return False, dndata
    bf_pm1 = 0
    bf_pm2d5 = 0
    bf_pm10 = 0
    num = len(rdata)
    upcount = 0
    for i in rdata:
        bf_pm1 = bf_pm1 + i['pm1']
        bf_pm2d5 = bf_pm2d5 + i['pm2d5']
        bf_pm10 = bf_pm10 + i['pm10']
        if 'day' == typeid:
            upcount = upcount + i['updatecount']
    if 'hour' == typeid:
        upcount = num
        
    return True, [ upcount, int(bf_pm1/num), int(bf_pm2d5/num), int(bf_pm10/num)]

def update_data( typeid, endtime):
    # set param
    if 'hour' ==  typeid:
        config_key = 'uptime_hour'
        adata_type = 3
        step_number = 3600
    elif 'day' == typeid:
        config_key = 'uptime_day'
        adata_type = 4
        step_number = 3600*24
    else:
        return False, 'Unknown type : %s'%typeid

    # get starttime
    sql = 'select unix_timestamp(dtime) as dtime from config where skey = "%s"'%config_key
    rflag, tdata = sql_read(sql)
    if not rflag:
        return False, tdata
    starttime = tdata[0]['dtime']

    # check
    stepcount = int((endtime - starttime)/step_number)
    if 0 == stepcount:
        return True, ''
    print typeid, stepcount, starttime, endtime

    # update data
    for i in range(stepcount):
        stime = starttime + (step_number*i)
        etime = starttime + (step_number*(i+1))
        print 'Get data %d - %d '%(stime, etime)
        # get devicename list
        rflag, dndata = get_clientid( typeid, stime, etime)
        if not rflag:
            return False, dndata
        # get data
        sqllist = []
        for dn in dndata:
            a=time.time()
            rflag, avgdata = get_avg_s2e( typeid, dn, stime, etime)
            #print 'mysql:%d'%(time.time()-a)
            if not rflag:
                return False, avgdata
            sqllist.append([ dn, adata_type, stime] + avgdata)
        print sqllist
        sql_updata = 'replace aggregate_data ( clientid, utype, starttime, updatecount, pm1, pm2d5, pm10) \
                values (%s, %s, from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s"), %s, %s, %s, %s)'
        rflag, rinfo = sql_exec( sql_updata, sqllist)
        if not rflag:
            return False, rinfo
        # update uptime
        print 'update next starttime %s - %d'%(config_key,etime)
        sql_uptime = 'update config set dtime = from_unixtime(%s,"%%Y-%%m-%%d %%H:%%i:%%s") where skey = %s'
        rflag, rinfo = sql_exec( sql_uptime, [[etime, config_key]])
        if not rflag:
            return False, rinfo
    return True, ''

def main_handler(event, context):
    # base test
    #print sql_read('select * from config')

    # get endtime
    endtime = int(time.time())
    print endtime

    rflag, rinfo = update_data( 'hour', endtime)
    if not rflag:
        print rinfo
        return False

    rflag, rinfo = update_data( 'day', endtime)
    if not rflag:
        print rinfo
        return False

    return True

