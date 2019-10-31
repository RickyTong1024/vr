#!/usr/bin/env python  
#coding=utf-8

import urllib
import httplib2
import json
import db
import time
import config
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

def sbytes2string(sbytes):
    al = []
    for i in range(0, len(sbytes), 2):
        al.append(chr(int(sbytes[i: i + 2], 16)))
    return ''.join(al)

def sbytes2int(sbytes):
    s = ''
    for i in range(0, len(sbytes), 2):
        s = sbytes[i: i + 2] + s
    if s == '':
        return '0'
    n = int(s, 16)
    return str(n)

def sbytes2addr(value):
    sbytes = value['value']
    s = ''
    for i in range(0, len(sbytes), 2):
        s = sbytes[i: i + 2] + s
    s = '0x' + s
    try:
        h = UInt160.ParseString(s)
        return Crypto.ToAddress(h)
    except:
        return ""

def get_value(value):
    tp = value['type']
    sbytes = value['value']
    if tp == 'ByteArray':
        return sbytes2int(sbytes)
    return sbytes

def makeRpcPostBodyT(method, params):
    body = {};
    body["jsonrpc"] = "2.0"
    body["method"] = method
    body["params"] = params
    body["id"] = 1
    return body

def post(body):
    headerdata = {"Content-type": "application/json"}
    body = json.dumps(body)
    conn = httplib2.Http(timeout=10)
    resp, content = conn.request(config.api, "POST", body, headers=headerdata) 
    return content

def getcliblockcount():
    body = makeRpcPostBodyT("getcliblockcount", [])
    content = post(body)
    content = json.loads(content)
    return int(content["result"][0]["cliblockcount"]) - 1

def getblock(block_id):
    body = makeRpcPostBodyT("getblock", [block_id])
    content = post(body)
    content = json.loads(content)
    txsc = content["result"][0]['tx']
    txs = []
    for i in range(len(txsc)):
        if txsc[i]['type'] == "InvocationTransaction":
            txs.append(txsc[i]['txid'])
    return txs

def getnotify(txid):
    if db.has_txid(txid):
       return 
    body = makeRpcPostBodyT("getnotify", [txid])
    content = post(body)
    content = json.loads(content)
    executions = content["result"][0]["executions"]
    for i in range(len(executions)):
        notifications = executions[i]["notifications"]
        for j in range(len(notifications)):
            contract = notifications[j]["contract"]
            state = notifications[j]["state"]
            if contract == config.fishHash:
                values = []
                for k in range(len(state["value"])):
                    values.append(state["value"][k])
                name = sbytes2string(values[0]["value"])
                senddata = {}
                senddata["cmd"] = name
                if name == "mine":
                    senddata["oid"] = get_value(values[1])
                    senddata["num"] = get_value(values[2])
                    db.add_op(senddata);
                elif name == "transfer":
                    senddata["from"] = sbytes2addr(values[1])
                    senddata["to"] = sbytes2addr(values[2])
                    senddata["value"] = get_value(values[3])
                    senddata["confirm"] = 0
                    senddata["time"] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    if senddata["from"] != "":
                        if senddata["to"] == config.server_addr:
                            db.add_op(senddata);
                            print(senddata)
    db.save_txid(txid)

def main():
    #db.init()
    while True:
        try:
            cli_num = getcliblockcount()
            num = db.get_blocknum()
            while num < cli_num:
                try:
                    tnum = num + 1
                    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "deal %d" % (tnum))
                    txs = getblock(tnum)
                    for i in range(len(txs)):
                        getnotify(txs[i])
                    db.set_blocknum(tnum)
                    num = num + 1
                except Exception as e:
                    print(e)
                    print("errors happened sleep 5s...")
                    time.sleep(5)
        except Exception as e:
            print(e)
            print("errors happened sleep 5s...")
            time.sleep(4)
        time.sleep(1)

if __name__ == '__main__':
    main()
    #print(getcliblockcount())

