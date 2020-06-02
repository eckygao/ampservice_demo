# -*- coding: utf8 -*-
import logging
import sys
import json
import base64

from ampmysql import AmpMysql

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

# init db connect
g_db = AmpMysql( 'IP', 'USER', 'PASSWORD', 00000, u'db')
g_db.connect();

print("connect database")

def get_30d_data( dbobj, clientid):
    # select clientid, spaceid
    sql = 'select date_format(starttime,"%%Y-%%m-%%d %%H:%%i:%%s") as x, PM1, PM2d5, PM10 from aggregate_data where utype = 3 and clientid = "%s" and starttime > date_sub(now(),interval 30 DAY) order by starttime asc '%(clientid)
    print sql
    rflag, rdata = dbobj.sql_read(sql)
    if not rflag:
        return False, dbobj.get_errorinfo()

    datalist = []
    for i in rdata:
        datalist.append({'x':i['x'], 'y':i['PM1'], 's':'PM1'})
        datalist.append({'x':i['x'], 'y':i['PM2d5'], 's':'PM2d5'})
        datalist.append({'x':i['x'], 'y':i['PM10'], 's':'PM10'})
    return True, json.dumps(datalist)

def get_30d_count( dbobj, clientid):
    # select clientid, spaceid
    sql = 'select "time" as s, date_format(starttime,"%%Y-%%m-%%d %%H:%%i:%%s") as x, updatecount as y from aggregate_data where utype = 3 and clientid = "%s" and starttime > date_sub(now(),interval 30 DAY) order by starttime asc '%(clientid)
    print sql
    rflag, rdata = dbobj.sql_read(sql)
    if not rflag:
        return False, dbobj.get_errorinfo()
    return True, json.dumps(rdata)

def get_devicename( dbobj, clientid):
    # select clientid, spaceid
    sql = 'select devicename from client where uid = "%s"'%(clientid)
    print sql
    rflag, rdata = dbobj.sql_read(sql)
    if not rflag:
        return False, dbobj.get_errorinfo()
    return True, json.dumps(rdata)

def get_constant_data( dbobj, clientid):
    # select clientid, spaceid
    sql = 'select date_format(time,"%%Y-%%m-%%d %%H:%%i:%%s") as x, PM1 , PM2d5, PM10 from base_data where clientid = "%s" and time > date_sub(now(),interval 3600 MINUTE_SECOND) order by time asc '%(clientid)
    print sql
    rflag, rdata = dbobj.sql_read(sql)
    if not rflag:
        return False, dbobj.get_errorinfo()

    datalist = []
    for i in rdata:
        datalist.append({'x':i['x'], 'y':i['PM1'], 's':'PM1'})
        datalist.append({'x':i['x'], 'y':i['PM2d5'], 's':'PM2d5'})
        datalist.append({'x':i['x'], 'y':i['PM10'], 's':'PM10'})
    return True, json.dumps(datalist)

def main_handler(event, context):
    # base format
    rdata = { 'isBase64Encoded': False,'statusCode': 200,'headers': {"Content-Type":"text/html"},'body': ''}
    # get post data
    print event
    # getkey
    keylist = event['queryString'].keys()
    if 'clientid' not in keylist or 'type' not in keylist:
        rdata['body'] = 'Lost param:%s'%(keylist)
        print rdata['body']
        return rdata
    clientid = int(event['queryString']['clientid'])
    datatype = event['queryString']['type']
    
    # check db
    global g_db
    if not g_db.check_connect():
        rdata['body'] = 'DB error:%s'%(g_db.get_errorinfo())
        print rdata['body']
        return rdata

    # funclist
    funclist = {
        '30d_data':get_30d_data, 
        '30d_count':get_30d_count,
        'constant':get_constant_data, 
        'devicename':get_devicename
        }
    if datatype not in funclist.keys():
        rdata['body'] = 'Error type:%s'%(datatype)
        print rdata['body']
        return rdata
    
    # get data
    rflag, rinfo = funclist[datatype]( g_db, clientid)
    rdata['statusCode'] = 200 if rflag else 409
    rdata['body'] = rinfo
    print rdata['body']

    return rdata