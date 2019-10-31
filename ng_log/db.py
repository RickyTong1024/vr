#!/usr/bin/env python  
#coding=utf-8

import time
import pymongo
import config
import urllib
import http.client
import json

g_conn = pymongo.MongoClient('127.0.0.1', 27017)
g_logdb = g_conn.logdb

MAX_AUTO_RECONNECT_ATTEMPTS = 5

def graceful_auto_reconnect(mongo_op_func):
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_AUTO_RECONNECT_ATTEMPTS):
            try:
                return mongo_op_func(*args, **kwargs)
            except pymongo.errors.AutoReconnect:
                print("reconnect time:%s", attempt + 1)
                wait_t = 0.5 * pow(2, attempt)
                time.sleep(wait_t)
    return wrapper

@graceful_auto_reconnect
def init():
    try:
        g_logdb.create_collection("block_num");
    except:
        pass
    try:
        g_logdb.create_collection("txid");
    except:
        pass
    g_logdb.txid.create_index("txid");
    try:
        g_logdb.create_collection("mine_op");
    except:
        pass
    g_logdb.mine_op.create_index("oid");
    try:
        self._logdb.create_collection("mine_op_num");
    except:
        pass
    try:
        g_logdb.create_collection("recharge_op");
    except:
        pass
    g_logdb.recharge_op.create_index("confirm");
   
@graceful_auto_reconnect
def get_blocknum():
    res = g_logdb.block_num.find_one()
    if res == None:
        g_logdb.block_num.insert({"block_num":config.init_block})
        return config.init_block
    return res['block_num']

@graceful_auto_reconnect
def set_blocknum(num):
    g_logdb.block_num.update_one({}, {"$set":{"block_num":num}})

@graceful_auto_reconnect
def has_txid(txid):
    res = g_logdb.txid.find_one({"txid":txid})
    return res != None

@graceful_auto_reconnect
def save_txid(txid):
    g_logdb.txid.insert({"txid":txid})

@graceful_auto_reconnect
def add_op(data):
    if data["cmd"] == "mine":
        res = g_logdb.mine_op.find_one({"oid" : data["oid"]})
        if res == None:
            g_logdb.mine_op.insert_one(data)
    else:
        g_logdb.recharge_op.insert_one(data)
    try:
        sendDataToapi(data)
    except:
        pass

def sendDataToapi(data):
    headerdata = {"Content-type": "application/json"}
    del data['_id']
    body = json.dumps(data)
    conn = http.client.HTTPConnection("127.0.0.1:10800", timeout = 20)
    try:
        conn.request("POST", "/ngupdate", body, headerdata)
    except Exception as e:
        print("http exception:", e)
    conn.close()
