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

def put_data(data, devicename):
    # check data
    if 0 == len(data):
        return False, "No data to insert"
    # cdb
    global g_db
    if not g_db.check_connect():
        return False, g_db.get_errorinfo()

    # basedata
    idata = []
    idata.append(data['PM1_CF1'])
    idata.append(data['PM2d5_CF1'])
    idata.append(data['PM10_CF1'])
    idata.append(data['PM1'])
    idata.append(data['PM2d5'])
    idata.append(data['PM10'])
    idata.append(data['particles_0d3'])
    idata.append(data['particles_0d5'])
    idata.append(data['particles_1'])
    idata.append(data['particles_2d5'])
    idata.append(data['particles_5'])
    idata.append(data['particles_10'])
    idata.append(data['version'])
    idata.append(data['Error']) 

    # select clientid, spaceid
    sql = 'select uid, spaceid from client where devicename = "%s"'%(devicename)
    rflag, rdata = g_db.sql_read(sql)
    if not rflag:
        return False, g_db.get_errorinfo()

    # check exists client
    if 0 != len(rdata):
        idata.append( rdata[0]['uid'])
        idata.append( rdata[0]['spaceid'])
        sql = "insert into base_data      (PM1_CF1, PM2d5_CF1, PM10_CF1, PM1, PM2d5, PM10, particles_0d3, particles_0d5, particles_1, particles_2d5, particles_5, particles_10, version, Error, clientid, spaceid) values ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)";
    else:
        idata.append( devicename)
        sql = "insert into temp_base_data (PM1_CF1, PM2d5_CF1, PM10_CF1, PM1, PM2d5, PM10, particles_0d3, particles_0d5, particles_1, particles_2d5, particles_5, particles_10, version, Error, devicename) values ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)";
    # insert into db
    print sql
    print idata

    if not g_db.sql_exec(sql, [idata]):
        print g_db.get_errorinfo()
        return False, g_db.get_errorinfo()
    return True, 'Success'

def main_handler(event, context):
    # base format
    rdata = { 'isBase64Encoded': False,'statusCode': 200,'headers': {"Content-Type":"text/html"},'body': ''}
    # get post data
    print event
    if 'body' not in event:
        rdata['statusCode'] = 409
        rdata['body'] = 'Lost post data';
        print rdata['body']
        return rdata

    # get data
    pdata = ''
    try:
        pdata = json.loads(event['body'])
    except:
        rdata['statusCode'] = 409
        rdata['body'] = 'post not json';
        print rdata['body']
        return rdata
    realdata = json.loads(base64.b64decode(pdata['payload']))

    # insert data
    adddata = realdata['params']
    rflag, rinfo = put_data( adddata, pdata['devicename'])
    rdata['statusCode'] = 200 if rflag else 409
    rdata['body'] = rinfo
    print rdata['body']

    return rdata