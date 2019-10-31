#!/usr/bin/env python  
#coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.web
import sys
import pymysql
import random
import json
import binascii

db = []
for i in range(20):
    db.append(None)

def create_db(index):
    global db
    db[index] = pymysql.connect(user='root', passwd='root', db='gwsnuser' + str(index), host='127.0.0.1')
    db[index].autocommit(1)

def ping(index):
    global db
    try:
        db[index].ping()
    except Exception as e:
        create_db(index)

def get_index(s):
    return binascii.crc32(s.encode('utf-8')) % 20
        
class regitser_handler(tornado.web.RequestHandler):
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        index = get_index(username)

        print("username:%s    password:%s    index:%d" % (username, password, index))

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return
        
        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return

        ping(index)
        cur = db[index].cursor()
        sql = "select password from user where username = %s"
        param = (username,)
        cur.execute(sql, param)
        res = cur.fetchall()

        if len(res) >= 1:
            # 账号重复
            print("chongfu error -1")
            self.write('{"result":"-1"}')
            self.finish()
            return

        sql = "insert into user (username, password, data) values(%s, %s, %s)"
        param = (username, password, "")
        cur.execute(sql, param)
        # 注册成功
        print("register suc 1")
        self.write('{"result":"0"}')
        self.finish()

class load_handler(tornado.web.RequestHandler):
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        index = get_index(username)

        print("username:%s    password:%s    index:%d" % (username, password, index))

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return
        
        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return

        ping(index)
        cur = db[index].cursor()
        sql = "select password, data from user where username = %s"
        param = (username,)
        cur.execute(sql, param)
        res = cur.fetchall()

        if len(res) > 1:
            # 未知问题
            print("unknow error -2")
            self.write('{"result":"-2"}')
            self.finish()
            return
        elif len(res) == 0:
            # 未注册
            print("register error -4")
            self.write('{"result":"-4"}')
            self.finish()
            return
        else:
            pw = res[0][0]
            data = res[0][1]
            if pw != password:
                # 密码错误
                print("password error -1")
                self.write('{"result":"-1"}')
                self.finish()
                return
            else:
                # 成功
                self.write('{"result":"0", "data":"%s"}' % (data,))
                self.finish()

class save_handler(tornado.web.RequestHandler):
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        data = self.get_body_argument("data")
        index = get_index(username)

        print("username:%s    password:%s    index:%d" % (username, password, index))

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return

        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return

        l = len(data)
        if l > 20 * 1024:
            # 长度问题
            print("len error -3")
            self.write('{"result":"-3"}')
            self.finish()
            return

        ping(index)
        cur = db[index].cursor()
        sql = "select password from user where username = '%s'" % (username)
        cur.execute(sql)
        res = cur.fetchall()

        if len(res) > 1:
            # 未知问题
            print("unknow error -2")
            self.write('{"result":"-2"}')
            self.finish()
            return
        elif len(res) == 0:
            # 未注册
            print("register error -4")
            self.write('{"result":"-4"}')
            self.finish()
            return
        else:
            pw = res[0][0]
            if pw != password:
                # 密码错误
                print("password error -1")
                self.write('{"result":"-1"}')
                self.finish()
                return
            
            sql = "update user set data = %s where username = %s"
            param = (data, username,)
            cur.execute(sql, param)
            # 成功
            print("save suc 0")
            self.write('{"result":"0"}')
            self.finish()
        
class Application(tornado.web.Application):  
    def __init__(self):  
        handlers = [
            (r"/regsiter", regitser_handler),
            (r"/load", load_handler),
            (r"/save", save_handler),
        ]
        tornado.web.Application.__init__(self, handlers)

def main():
    port = 10001
    if len(sys.argv) > 1:
        port = sys.argv[i]
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port)
    print('Welcome to the machine...')
    tornado.ioloop.IOLoop.instance().start()
            
if __name__ == '__main__':
    main()

