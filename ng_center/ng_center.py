#!/usr/bin/env python  
#coding=utf-8

import sys
import config
import tornado.httpserver
import tornado.ioloop
import tornado.web
import json
from ng_mine import ng_mine
from ng_user import ng_user
from ng_dress import ng_dress
from ng_auction import ng_auction
import ng_tool

class base_handler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(base_handler, self).__init__(*args, **kwargs)
        self._args = {}
        self._argl = []

    def dbug(self):
        print(self.__class__.__name__, self.request.body)
    
    def check_arguments(self):
        for i in range(len(self._argl)):
            a = self.get_argument(self._argl[i], None)
            self._args[self._argl[i]] = a
            if a == None:
                return False
        return True

    def check_user(self, check_admin = False):
        return ng_user.instance().check(self._args["user_id"], self._args["token"], check_admin)
        

    def end(self, res, debug = True):
        if debug:
            print(res)
        self.write(res)
        self.finish()

    def end_ex(self, res, param = None):
        res = ng_tool.make_result(res, param)
        print(res)
        self.write(res)
        self.finish()

class ngupdate_handler(tornado.web.RequestHandler):
    def post(self):

        data = json.loads(self.request.body)
            
        self.write("1")
        self.finish()       

class login_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["address", "wif", "name", "gas"]
        if not self.check_arguments():
            self.end_ex(1)
            return
        
        user_id, token = ng_user.instance().login(self._args["address"], self._args["wif"], self._args["name"], self._args["gas"])
        self.end_ex(0, {"user_id" : user_id, "token" : token})

class user_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_user.instance().view(self._args["user_id"])
        self.end(res)

class user_view_data_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_user.instance().view_data(self._args["user_id"])
        self.end(res)

class user_modify_data_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "param"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_user.instance().modify_data(self._args["user_id"], self._args["param"])
        self.end(res)

class user_refund_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "num"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_user.instance().refund(self._args["user_id"], self._args["num"])
        self.end(res)

class user_use_fish_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "num"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_user.instance().use_fish(self._args["user_id"], self._args["num"])
        self.end(res)

class captcha_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_mine.instance().captcha(self._args["user_id"])
        self.end(res, False)

class mine_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "code"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_mine.instance().mine(self._args["user_id"], self._args["code"])
        self.end(res)

class mine_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_mine.instance().mine_view(self._args["user_id"])
        self.end(res)

########################################################################

class dress_create_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "dress_type"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user(True):
            self.end_ex(2)
            return

        res = ng_dress.instance().dress_create(self._args["user_id"], self._args["dress_type"])
        self.end(res)

class dress_modify_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "dress_id", "dress_type"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user(True):
            self.end_ex(2)
            return

        res = ng_dress.instance().dress_modify(self._args["dress_id"], self._args["dress_type"])
        self.end(res)

class dress_transfer_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "dress_id", "address"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return
        res = ng_dress.instance().dress_transfer(self._args["user_id"], self._args["dress_id"], self._args["address"])
        self.end(res)
        
class dress_user_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "page"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_dress.instance().dress_user_view(self._args["user_id"], self._args["page"])
        self.end(res)
           
class dress_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "dress_id"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_dress.instance().dress_view(self._args["dress_id"])
        self.end(res)
        
########################################################################

class auction_user_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "page"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_user_view(self._args["user_id"], self._args["page"])
        self.end(res)

class auction_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "auction_id"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_view(self._args["user_id"], self._args["auction_id"])
        self.end(res)

class auction_list_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "page", "sort"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_list(self._args["user_id"], self._args["page"], self._args["sort"])
        self.end(res)

class auction_start_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "dress_id", "bp", "ep", "duration"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_start(self._args["user_id"], self._args["dress_id"], self._args["bp"], self._args["ep"], self._args["duration"])
        self.end(res)

class auction_cancel_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "auction_id"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_cancel(self._args["user_id"], self._args["auction_id"])
        self.end(res)

class auction_buy_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "auction_id"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_buy(self._args["user_id"], self._args["auction_id"])
        self.end(res)

class auction_follow_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "auction_id", "follow"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_follow(self._args["user_id"], self._args["auction_id"], self._args["follow"])
        self.end(res)

class auction_follow_view_handler(base_handler):
    def post(self):
        self.dbug()

        self._argl = ["user_id", "token", "page"]
        if not self.check_arguments():
            self.end_ex(1)
            return            
        if not self.check_user():
            self.end_ex(2)
            return

        res = ng_auction.instance().auction_follow_view(self._args["user_id"], self._args["page"])
        self.end(res)
        
########################################################################

class Application(tornado.web.Application):
    def __init__(self):  
        handlers = [
            (r"/ngupdate", ngupdate_handler),
            (r"/login", login_handler),
            (r"/user_view", user_view_handler),
            (r"/user_modify_data", user_modify_data_handler),
            (r"/user_view_data", user_view_data_handler),
            (r"/user_refund", user_refund_handler),
            (r"/user_use_fish", user_use_fish_handler),
            
            (r"/captcha", captcha_handler),
            (r"/mine", mine_handler),
            (r"/mine_view", mine_view_handler),
            
	    (r"/dress_create", dress_create_handler),
            (r"/dress_modify", dress_modify_handler),
            (r"/dress_transfer", dress_transfer_handler),
            (r"/dress_user_view", dress_user_view_handler),
            (r"/dress_view", dress_view_handler),
            
            (r"/auction_user_view", auction_user_view_handler),
            (r"/auction_view", auction_view_handler),
            (r"/auction_list", auction_list_handler),
            (r"/auction_start", auction_start_handler),
            (r"/auction_cancel", auction_cancel_handler),
            (r"/auction_buy", auction_buy_handler),
            (r"/auction_follow", auction_follow_handler),
            (r"/auction_follow_view", auction_follow_view_handler),
        ]
        tornado.web.Application.__init__(self, handlers)
        
def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(config.port)
    print('Welcome to the machine...')

    ng_mine.instance().start()
    ng_auction.instance().update()
    tornado.ioloop.IOLoop.instance().start()
            
if __name__ == '__main__':
    main()
