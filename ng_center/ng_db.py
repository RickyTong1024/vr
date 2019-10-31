#!/usr/bin/env python  
#coding=utf-8

import time
import pymongo
from ng_instance import *
import config

MAX_AUTO_RECONNECT_ATTEMPTS = 5

def graceful_auto_reconnect(mongo_op_func):
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_AUTO_RECONNECT_ATTEMPTS):
            try:
                return mongo_op_func(*args, **kwargs)
            except pymongo.errors.AutoReconnect:
                wait_t = 0.5 * pow(2, attempt)
                time.sleep(wait_t)
    return wrapper

class ng_db(ng_instance):
    def __init__(self):
        self._conn = pymongo.MongoClient('127.0.0.1', 27017)
        self._ngdb = self._conn.ngdb
        self._logdb = self._conn.logdb
        self._jsdb = self._conn.jsdb

        self.init()

    @graceful_auto_reconnect
    def init(self):
        try:
            self._ngdb.create_collection("user_num");
        except:
            pass
        try:
            self._ngdb.create_collection("user");
        except:
            pass
        self._ngdb.user.create_index("user_id");
        self._ngdb.user.create_index("address");
        try:
            self._ngdb.create_collection("user_data");
        except:
            pass
        self._ngdb.user_data.create_index("user_id");
        
        try:
            self._ngdb.create_collection("dress_num");
        except:
            pass
        try:
            self._ngdb.create_collection("dress");
        except:
            pass
        self._ngdb.dress.create_index("dress_id");
        
        try:
            self._ngdb.create_collection("auction_num");
        except:
            pass
        try:
            self._ngdb.create_collection("auction");
        except:
            pass
        self._ngdb.auction.create_index("auction_id");
        self._ngdb.auction.create_index("user_id");
        
        try:
            self._ngdb.create_collection("follow");
        except:
            pass
        self._ngdb.follow.create_index("auction_id");
        self._ngdb.follow.create_index("user_id");
        
        try:
            self._ngdb.create_collection("remain");
        except:
            pass

    @graceful_auto_reconnect
    def get_num(self, col):
        res = col.find_one()
        if res == None:
            col.insert_one({"num" : 1})
            return 0
        else:
            col.update_one({}, {'$set' : {"num" : res["num"] + 1}})
            return res["num"]

    @graceful_auto_reconnect
    def mine_seek(self):
        res = self._logdb.mine_op_num.find_one()
        if res == None:
            self._logdb.mine_op_num.insert_one({"oid" : 0})
            return self.mine_deal(0, {"oid" : "0"})
        else:
            return self.mine_deal(res["oid"], {"oid" : str(res["oid"])})

    @graceful_auto_reconnect
    def mine_deal(self, oid, param):
        res = self._logdb.mine_op.find_one(param)
        if res != None:
            self._logdb.mine_op_num.update_one({}, {'$set' : {"oid" : oid + 1}})
        return res

    @graceful_auto_reconnect
    def remain_add_fish(self, num):
        res = self._ngdb.remain.find_one({})
        if res != None:
            self._ngdb.remain.update_one({}, {'$set' : {"fish" : res['fish'] + num}})
        else:
            self._ngdb.remain.insert_one({"fish" : num})

    @graceful_auto_reconnect
    def remain_refund(self):
        res = self._ngdb.remain.find_one({})
        if res != None:
            self._ngdb.remain.update_one({}, {'$set' : {"fish" : 0}})
            num = res["fish"]
            if num > 0:
                self.refund("", num)

    @graceful_auto_reconnect
    def user_add_fish(self, user_id, num):
        res = self._ngdb.user.find_one({"user_id" : user_id})
        if res != None:
            self._ngdb.user.update_one({"user_id" : user_id}, {'$set' : {"fish" : res['fish'] + num}})

    @graceful_auto_reconnect
    def user_login(self, address, wif, name, gas):
        res = self._ngdb.user.find_one({"address" : address})
        if res == None:
            num = self.get_num(self._ngdb.user_num)
            res = {
                "user_id" : str(num + 1),
                "address" : address,
                "wif" : wif,
                "name" : name,
                "fish" : 0,
                "gas" : gas,
                }
            self._ngdb.user.insert_one(res)
        else:
            self._ngdb.user.update_one({"address" : address}, {'$set' : {"wif" : wif, "name" : name, "gas" : gas}})
        return res

    @graceful_auto_reconnect
    def user_get(self, user_id):
        res = self._ngdb.user.find_one({"user_id" : user_id}, {'_id' :0})
        return res

    @graceful_auto_reconnect
    def user_get_by_address(self, address):
        res = self._ngdb.user.find_one({"address" : address}, {'_id' :0})
        return res

    @graceful_auto_reconnect
    def user_get_data(self, user_id):
        res = self._ngdb.user_data.find_one({"user_id" : user_id}, {'_id' :0})
        if res == None:
            res = {"user_id" : user_id}
        return res

    @graceful_auto_reconnect
    def user_modify_data(self, user_id, param):
        res = self._ngdb.user_data.find_one({"user_id" : user_id}, {'_id' :0})
        if res == None:
            self._ngdb.user_data.insert_one({"user_id" : user_id})
        self._ngdb.user_data.update_one({"user_id" : user_id}, {'$set' : param})

    @graceful_auto_reconnect
    def user_refund(self, user_id, num):
        res = self._ngdb.user.find_one({"user_id" : user_id})
        if res:
            self._ngdb.user.update_one({"user_id" : user_id}, {'$set' : {"fish" : res['fish'] - num}})
            self.refund(res["address"], num)

    @graceful_auto_reconnect
    def recharge_check(self):
        res = self._logdb.recharge_op.find({"confirm" : 0})
        for recharge in res:
            address = recharge["from"]
            user = self._ngdb.user.find_one({"address" : address})
            if user != None:
                self._ngdb.user.update_one({"address" : address}, {'$set' : {"fish" : user['fish'] + int(recharge['value'])}})
            self._logdb.recharge_op.update_one({"_id" : recharge["_id"]}, {'$set' : {"confirm" : 1}})

    @graceful_auto_reconnect
    def refund(self, user_id, num):
        self._jsdb.refund.insert_one({"who" : user_id, "num" : num, "confirm" : 0, "transaction" : "", "last_time" : 0})

    @graceful_auto_reconnect
    def dress_get(self):
        res = self._ngdb.dress.find({}, {'_id' :0})
        return res
    
    @graceful_auto_reconnect
    def dress_create(self, user_id, dress_type):
        num = self.get_num(self._ngdb.dress_num)
        dress = {
            "dress_id" : str(num + 1),
            "dress_type" : dress_type,
            "user_id" : user_id,
            }
        self._ngdb.dress.insert_one(dress)
        del dress["_id"]
        return dress

    @graceful_auto_reconnect
    def dress_modify(self, dress_id, param):
        res = self._ngdb.dress.find_one({"dress_id" : dress_id})
        if res != None:
            self._ngdb.dress.update_one({"dress_id" : dress_id}, {'$set' : param})

    @graceful_auto_reconnect
    def auction_get(self):
        res = self._ngdb.auction.find({}, {'_id' :0})
        return res
    
    @graceful_auto_reconnect
    def auction_create(self, dress_id, dress_type, user_id, name, bp, ep, duration):
        num = self.get_num(self._ngdb.auction_num)
        auction = {
            "auction_id" : str(num + 1),
            "dress_id" : dress_id,
            "dress_type" : dress_type,
            "user_id" : user_id,
            "name" : name,
            "bp" : bp,
            "ep" : ep,
            "duration" : duration,
            "selltime" : int(time.time()),
            "follow" : 0,
            }
        self._ngdb.auction.insert_one(auction)
        del auction['_id']
        return auction

    @graceful_auto_reconnect
    def auction_delete(self, auction_id):
        self._ngdb.auction.remove({"auction_id" : auction_id})

    @graceful_auto_reconnect
    def acution_modify(self, auction_id, param):
        res = self._ngdb.auction.find_one({"auction_id" : auction_id})
        if res != None:
            self._ngdb.auction.update_one({"auction_id" : auction_id}, {'$set' : param})

    @graceful_auto_reconnect
    def follow_get(self):
        res = self._ngdb.follow.find({}, {'_id' :0})
        return res
    
    @graceful_auto_reconnect
    def follow_create(self, user_id, auction_id):
        return self._ngdb.follow.insert_one({"user_id" : user_id, "auction_id" : auction_id})

    @graceful_auto_reconnect
    def follow_delete(self, user_id, auction_id):
        return self._ngdb.follow.remove({"user_id" : user_id, "auction_id" : auction_id})

    @graceful_auto_reconnect
    def follow_delete_all(self, auction_id):
        return self._ngdb.follow.remove({"auction_id" : auction_id})

