#!/usr/bin/env python  
#coding=utf-8

from ng_instance import *
from ng_db import ng_db
import ng_tool
import config

class ng_dress(ng_instance):
    def __init__(self):
        self._dress_info = {}
        self._user_dress = {}
        res = ng_db.instance().dress_get()
        for dress in res:
            user_id = dress["user_id"]
            self.cache_dress_add(user_id, dress)

    def cache_dress_add(self, user_id, dress):
        dress_id = dress["dress_id"]
        if not user_id in self._user_dress:
            self._user_dress[user_id] = []
        self._user_dress[user_id].append(dress_id)
        self._dress_info[dress_id] = dress

    def cache_dress_get(self, dress_id):
        if not dress_id in self._dress_info:
            return None
        return self._dress_info[dress_id]

    def cache_dress_transfer(self, dress_id, user_id):
        if not dress_id in self._dress_info:
            return
        if not user_id in self._user_dress:
            self._user_dress[user_id] = []
        self._user_dress[user_id].append(dress_id)
        old_user_id = self._dress_info[dress_id]["user_id"]
        self._user_dress[old_user_id].remove(dress_id)
        self._dress_info[dress_id]["user_id"] = user_id

    def dress_create(self, user_id, dress_type):
        dress = ng_db.instance().dress_create(user_id, dress_type)
        self.cache_dress_add(user_id, dress)
        return ng_tool.make_result(0, dress)

    def dress_modify(self, dress_id, dress_type):
        if not dress_id in self._dress_info:
            return ng_tool.make_result(-1)
        self._dress_info[dress_id]["dress_type"] = dress_type
        ng_db.instance().dress_modify(dress_id, {"dress_type" : dress_type})
        return ng_tool.make_result(0)

    def dress_transfer(self, user_id, dress_id, address):
        if not dress_id in self._dress_info:
            return ng_tool.make_result(-1)
        new_user = ng_db.instance().user_get_by_address(address)
        if new_user == None:
            return ng_tool.make_result(-2)
        new_user_id = new_user["user_id"]
        if user_id == new_user_id:
            return ng_tool.make_result(-3)
        dress = self._dress_info[dress_id]
        if dress["user_id"] != user_id:
            return ng_tool.make_result(-4)
        self.cache_dress_transfer(dress_id, new_user_id)
        ng_db.instance().dress_modify(dress_id, {"user_id" : new_user_id})
        return ng_tool.make_result(0)

    def dress_transfer_app(self, dress_id, user_id):
        if not dress_id in self._dress_info:
            return
        self.cache_dress_transfer(dress_id, user_id)
        ng_db.instance().dress_modify(dress_id, {"user_id" : user_id})

    def dress_user_view(self, user_id, page):
        page = int(page)
        dresses = []
        if not user_id in self._user_dress:
            return ng_tool.make_result(0, {"page_num" : 0, "dresses" : dresses})
        total_num = len(self._user_dress[user_id])
        page_num = int((total_num + config.page_size - 1) / config.page_size)
        for i in range((page - 1) * config.page_size, page * config.page_size):
            if i >= 0 and i < total_num:
                dress_id = self._user_dress[user_id][i]
                dresses.append(self._dress_info[dress_id])
        return ng_tool.make_result(0, {"page_num" : page_num, "dresses" : dresses})

    def dress_view(self, dress_id):
        if not dress_id in self._dress_info:
            return ng_tool.make_result(-1)
        return ng_tool.make_result(0, self._dress_info[dress_id])
