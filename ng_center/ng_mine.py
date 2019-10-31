#!/usr/bin/env python  
#coding=utf-8

import time
import tornado.ioloop
from ng_instance import *
from ng_db import ng_db
import ng_tool

MINE_TIME = 300

class ng_mine(ng_instance):
    def __init__(self):
        self._captcha = {}
        self._mine_list = {}
        self._last_list = {}

    def captcha(self, user_id):
        s, data = ng_tool.make_captcha()
        self._captcha[user_id] = s
        return data.read()

    def mine(self, user_id, code):
        if not user_id in self._captcha:
            return ng_tool.make_result(-1)
        if code.lower() != self._captcha[user_id].lower():
            del self._captcha[user_id]
            return ng_tool.make_result(-2)            
        if not user_id in self._mine_list:
            self._mine_list[user_id] = {"num" : 0, "start_time" : int(time.time())}
        return self.mine_view(user_id)

    def mine_view(self, user_id):
        data = {}
        data["mine_player_num"] = len(self._mine_list)
        if not user_id in self._mine_list:
            data["is_mine"] = 0
            data["num"] = 0
            data["start_time"] = 0
        else:
            data["is_mine"] = 1
            data["num"] = self._mine_list[user_id]['num']
            data["start_time"] = self._mine_list[user_id]['start_time']
        num = 0
        if user_id in self._last_list:
            num = self._last_list[user_id]
        data["last_num"] = num
        return ng_tool.make_result(0, data)

    def start(self):
        self.despatch()
        self.refund_reamin()

    def despatch(self):
        data = ng_db.instance().mine_seek()
        if data != None:
            mine_num = int(data['num'])
            mine_player_num  = len(self._mine_list)
            if mine_player_num > 0:
                every_mine_num  = int(mine_num / mine_player_num)
                remain_num = mine_num - every_mine_num * mine_player_num
                for user_id in self._mine_list:
                    user = self._mine_list[user_id]
                    user["num"] = user["num"] + every_mine_num
                if remain_num > 0:
                    ng_db.instance().remain_add_fish(remain_num)
            else:
                ng_db.instance().remain_add_fish(mine_num)

        now = time.time()
        remove_list = []
        for user_id in self._mine_list:
            user = self._mine_list[user_id]
            if user["start_time"] + MINE_TIME <= now:
                ng_db.instance().user_add_fish(user_id, user["num"])
                self._last_list[user_id] = user["num"]
                remove_list.append(user_id)

        for i in range(len(remove_list)):
            del self._mine_list[remove_list[i]]

        ng_db.instance().recharge_check()
                
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 3, self.despatch)

    def refund_reamin(self):
        ng_db.instance().remain_refund()
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 3600, self.refund_reamin)
