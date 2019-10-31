#!/usr/bin/env python  
#coding=utf-8

import random
from ng_instance import *
from ng_db import ng_db
import ng_tool
import json
import config

class ng_user(ng_instance):
    def __init__(self):
        self._users = {}
        
    def login(self, address, wif, name, gas):
        res = ng_db.instance().user_login(address, wif, name, gas)
        user_id = res["user_id"]
        token = self.make_token()
        self._users[user_id] = res
        self._users[user_id]["token"] = token
        return user_id, token

    def check(self, user_id, token, check_admin):
        if not user_id in self._users:
            return False
        if self._users[user_id]["token"] != token:
            return False
        if check_admin and self._users[user_id]["wif"] != config.admin_wif:
            return False
        return True

    def view(self, user_id):
        user = ng_db.instance().user_get(user_id)
        if user == None:
            return ng_tool.make_result(-1)
        return ng_tool.make_result(0, user)

    def view_data(self, user_id):
        user_data = ng_db.instance().user_get_data(user_id)
        if user_data == None:
            return ng_tool.make_result(-1)
        return ng_tool.make_result(0, user_data)

    def modify_data(self, user_id, param):
        param = json.loads(param)
        ng_db.instance().user_modify_data(user_id, param)
        return ng_tool.make_result(0)

    def refund(self, user_id, num):
        num = int(num)
        if num <= 0:
            return ng_tool.make_result(-1)
        user = ng_db.instance().user_get(user_id)
        if user == None:
            return ng_tool.make_result(-1)
        if user["fish"] < num:
            return ng_tool.make_result(-2)
        ng_db.instance().user_refund(user_id, num)
        return ng_tool.make_result(0)

    def use_fish(self, user_id, num):
        num = int(num)
        if num <= 0:
            return ng_tool.make_result(-1)
        user = ng_db.instance().user_get(user_id)
        if user == None:
            return ng_tool.make_result(-1)
        if user["fish"] < num:
            return ng_tool.make_result(-2)
        ng_db.instance().user_add_fish(user_id, -num)
        return ng_tool.make_result(0)

    def make_token(self):
        return str(random.randint(100000, 999999))
