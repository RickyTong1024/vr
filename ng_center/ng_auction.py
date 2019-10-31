#!/usr/bin/env python  
#coding=utf-8

from ng_instance import *
from ng_db import ng_db
from ng_dress import ng_dress
import ng_tool
from operator import itemgetter
import tornado.ioloop
import time
import config

class ng_auction(ng_instance):
    def __init__(self):
        self.TX_MIN_FEE = 5000000
        self._auction_info = {}
        self._user_auction = {}
        self._auction_sorts = []
        res = ng_db.instance().auction_get()
        for auction in res:
            user_id = auction["user_id"]
            self.cache_auction_add(user_id, auction)
        self._follow_user_auction = {}
        self._follow_auction_user = {}
        res = ng_db.instance().follow_get()
        for follow in res:
            user_id = follow["user_id"]
            auction_id = follow["auction_id"]
            self.cache_follow_add(user_id, auction_id)

    def cache_auction_add(self, user_id, auction):
        auction_id = auction["auction_id"]
        if not user_id in self._user_auction:
            self._user_auction[user_id] = []
        self._user_auction[user_id].append(auction_id)
        self._auction_info[auction_id] = auction

    def cache_auction_del(self, auction_id):
        if not auction_id in self._auction_info:
            return
        auction = self._auction_info[auction_id]
        user_id = auction["user_id"]
        if user_id in self._user_auction:
            self._user_auction[user_id].remove(auction_id)
        del self._auction_info[auction_id]

        if auction_id in self._follow_auction_user:
            for i in range(len(self._follow_auction_user[auction_id])):
                u = self._follow_auction_user[auction_id][i]
                self._follow_user_auction[u].remove(auction_id)
            del self._follow_auction_user[auction_id]
    
    def cache_follow_add(self, user_id, auction_id):
        if not user_id in self._follow_user_auction:
            self._follow_user_auction[user_id] = []
        self._follow_user_auction[user_id].append(auction_id)
        if not auction_id in self._follow_auction_user:
            self._follow_auction_user[auction_id] = []
        self._follow_auction_user[auction_id].append(user_id)

    def cache_follow_del(self, user_id, auction_id):
        if user_id in self._follow_user_auction:
            self._follow_user_auction[user_id].remove(auction_id)
        if auction_id in self._follow_auction_user:
            self._follow_auction_user[auction_id].remove(user_id)

    def cache_follow_has(self, user_id, auction_id):
        if user_id in self._follow_user_auction:
            return auction_id in self._follow_user_auction[user_id]
        return False

    def auction_user_view(self, user_id, page):
        page = int(page)
        auctions = []
        if not user_id in self._user_auction:
            return ng_tool.make_result(0, {"page_num" : 0, "auctions" : auctions})
        total_num = len(self._user_auction[user_id])
        page_num = int((total_num + config.page_size - 1) / config.page_size)
        for i in range((page - 1) * config.page_size, page * config.page_size):
            if i >= 0 and i < total_num:
                auction_id = self._user_auction[user_id][i]
                auctions.append(self._auction_info[auction_id])
        return ng_tool.make_result(0, {"page_num" : page_num, "auctions" : auctions})

    def auction_view(self, auction_id):
        if not auction_id in self._auction_info:
            return ng_tool.make_result(-1)
        return ng_tool.make_result(0, self._auction_info[auction_id])

    def auction_list(self, user_id, page, sort):
        page = int(page)
        sort = int(sort)
        if sort < 0 or sort >= 4:
            return ng_tool.make_result(-1)
        auctions = []
        ast = self._auction_sorts[sort]
        total_num = len(ast)
        page_num = int((total_num + config.page_size - 1) / config.page_size)
        for i in range((page - 1) * config.page_size, page * config.page_size):
            if i >= 0 and i < total_num:
                auction_id = ast[i][1]
                if auction_id in self._auction_info:
                    auctions.append(self._auction_info[auction_id])
                    if self.cache_follow_has(user_id, auction_id):
                        auctions[len(auctions) - 1]["is_follow"] = 1
                    else:
                        auctions[len(auctions) - 1]["is_follow"] = 0
        return ng_tool.make_result(0, {"page_num" : page_num, "total_num" : total_num, "auctions" : auctions})

    def auction_start(self, user_id, dress_id, bp, ep, duration):
        bp = int(bp)
        ep = int(ep)
        duration = int(duration)
        dress = ng_dress.instance().cache_dress_get(dress_id)
        if dress == None or dress["user_id"] != user_id:
            return ng_tool.make_result(-1)
        user = ng_db.instance().user_get(user_id)
        if user == None:
            return ng_tool.make_result(-2)
        if bp < 0 or ep < 0 or bp < ep:
            return ng_tool.make_result(-3)
        if ep < self.TX_MIN_FEE:
            return ng_tool.make_result(-3)
        
        auction = ng_db.instance().auction_create(dress_id, dress["dress_type"], user_id, user["name"], bp, ep, duration)
        self.cache_auction_add(user_id, auction)
        ng_dress.instance().dress_transfer_app(dress_id, "admin")
        return ng_tool.make_result(0)

    def auction_cancel(self, user_id, auction_id):
        if not auction_id in self._auction_info:
            return ng_tool.make_result(-1)
        auction = self._auction_info[auction_id]
        if user_id != auction["user_id"]:
            return ng_tool.make_result(-2)
        dress_id = auction["dress_id"]
        self.cache_auction_del(auction_id)
        ng_db.instance().auction_delete(auction_id)
        ng_db.instance().follow_delete_all(auction_id)
        ng_dress.instance().dress_transfer_app(dress_id, user_id)
        return ng_tool.make_result(0)

    def auction_buy(self, user_id, auction_id):
        if not auction_id in self._auction_info:
            return ng_tool.make_result(-1)
        auction = self._auction_info[auction_id]
        user = ng_db.instance().user_get(user_id)
        if user == None:
            return ng_tool.make_result(-2)
        seller_user_id = auction["user_id"]
        if user_id == seller_user_id:
            return ng_tool.make_result(-3)
        cp = self.calc_price(auction["bp"], auction["ep"], auction["duration"], auction["selltime"])
        fee = int(cp * 50 /1000)
        if cp < fee:
            cp = fee
        if user["fish"] < cp:
            return ng_tool.make_result(-4)
        ng_dress.instance().dress_transfer_app(auction["dress_id"], user_id)
        ng_db.instance().user_add_fish(user_id, -cp)
        sell_price = cp - fee
        ng_db.instance().user_add_fish(seller_user_id, sell_price)
        self.cache_auction_del(auction_id)
        ng_db.instance().auction_delete(auction_id)
        ng_db.instance().follow_delete_all(auction_id)
        return ng_tool.make_result(0)

    def auction_follow(self, user_id, auction_id, follow):
        if not auction_id in self._auction_info:
            return ng_tool.make_result(-1)
        auction = self._auction_info[auction_id]
        user = ng_db.instance().user_get(user_id)
        if user == None:
            return ng_tool.make_result(-2)
        has_followed = self.cache_follow_has(user_id, auction_id)
        if not has_followed and follow == "1":
            auction["follow"] = auction["follow"] + 1
            ng_db.instance().acution_modify(auction_id, {"follow" : auction["follow"]})
            self.cache_follow_add(user_id, auction_id)
            ng_db.instance().follow_create(user_id, auction_id)
        elif has_followed and follow == "0":
            auction["follow"] = auction["follow"] - 1
            ng_db.instance().acution_modify(auction_id, {"follow" : auction["follow"]})
            self.cache_follow_del(user_id, auction_id)
            ng_db.instance().follow_delete(user_id, auction_id)
        return ng_tool.make_result(0)
    
    def auction_follow_view(self, user_id, page):
        page = int(page)
        auctions = []
        if not user_id in self._follow_user_auction:
            return ng_tool.make_result(0, {"page_num" : 0, "auctions" : auctions})
        total_num = len(self._follow_user_auction[user_id])
        page_num = int((total_num + config.page_size - 1) / config.page_size)
        for i in range((page - 1) * config.page_size, page * config.page_size):
            if i >= 0 and i < total_num:
                auction_id = self._follow_user_auction[user_id][i]
                auctions.append(self._auction_info[auction_id])
        return ng_tool.make_result(0, {"page_num" : page_num, "auctions" : auctions})

    def update(self):
        self._auction_sorts = []
        sort1 = []
        sort2 = []
        sort3 = []
        sort4 = []
        for auction_id in self._auction_info:
            data = self._auction_info[auction_id]
            oid = data['auction_id']
            beginPrice = data['bp']
            endPrice = data['ep']
            duration = data['duration']
            sellTime = data['selltime']
            follow = data['follow']
            sort1.append([self.calc_price(beginPrice, endPrice, duration, sellTime), auction_id])
            sort2.append([self.calc_price(beginPrice, endPrice, duration, sellTime), auction_id])
            sort3.append([oid, auction_id])
            sort4.append([follow, auction_id])
        sort1 = sorted(sort1, key = itemgetter(0))
        sort2 = sorted(sort2, key = itemgetter(0), reverse=True)
        sort3 = sorted(sort3, key = itemgetter(0), reverse=True)
        sort4 = sorted(sort4, key = itemgetter(0), reverse=True)
        self._auction_sorts.append(sort1)
        self._auction_sorts.append(sort2)
        self._auction_sorts.append(sort3)
        self._auction_sorts.append(sort4)
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 10, self.update)

    def calc_price(self, b, e, d, st):
        sp = int(time.time()) - st
        if d < 1:
            d = 1
        if sp < 0:
            sp = 0
        elif sp >= d:
            sp = d
        np = b + (e - b) * sp / d
        np = int(np)
        return np
