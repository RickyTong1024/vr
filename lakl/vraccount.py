#!/usr/bin/env python  
#coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.web
import sys
import MySQLdb
import random
import json
import binascii

db = []
for i in range(20):
    db.append(None)

def get_code():
    return str(random.randint(1000, 10000))

def create_db(index):
    global db
    db[index] = MySQLdb.connect(user='root', passwd='root', db='lakluser' + str(i), host='127.0.0.1')

def ping(index):
    global db
    try:
        db[index].ping()
    except Exception,e:
        create_db(index)

def get_index(s):
    return binascii.crc32(s) % 20

class base_handler(tornado.web.RequestHandler):
    connection_closed = False

    def on_connection_close(self):
        self.connection_closed = True
        
class regitser_handler(base_handler):
    @tornado.web.asynchronous
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        index = get_index(username)

        print "username:%s    password:%s    index:%d" % (username, password, index)

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return
        
        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
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
            print "chongfu error -1"
            self.write('{"result":"-1"}')
            self.finish()
            return

        code = get_code()

        sql = "insert into user (username, password, data, code, dt) values(%s, %s, %s, %s, %s)"
        param = (username, password, "", code, 0)
        cur.execute(sql, param)
        # 注册成功
        print "register suc 1"
        self.write('{"result":"0", "code":"%s"}' % code)
        self.finish()

class load_handler(base_handler):
    @tornado.web.asynchronous
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        index = get_index(username)

        print "username:%s    password:%s    index:%d" % (username, password, index)

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return
        
        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return

        ping(index)
        cur = db[index].cursor()
        sql = "select password, data, dt, UNIX_TIMESTAMP() from user where username = %s"
        param = (username,)
        cur.execute(sql, param)
        res = cur.fetchall()

        if len(res) > 1:
            # 未知问题
            print "unknow error -2"
            self.write('{"result":"-2"}')
            self.finish()
            return
        elif len(res) == 0:
            # 未注册
            print "register error -4"
            self.write('{"result":"-4"}')
            self.finish()
            return
        else:
            pw = res[0][0]
            dt = res[0][2]
            dt1 = res[0][3]
            if pw != password:
                # 密码错误
                print "password error -1"
                self.write('{"result":"-1"}')
                self.finish()
                return
            elif dt != None and dt > dt1:
                #  锁定中
                print "lock error -5"
                self.write('{"result":"-5"}')
                self.finish()
            else:
                # 成功
                code = get_code()
                sql = "update user set code = %s where username = %s"
                param = (code, username,)
                cur.execute(sql, param)
                print "load suc 0"
                dt = res[0][1]
                self.write('{"result":"0", "data":"%s", "code":"%s"}' % (dt, code))
                self.finish()

class save_handler(base_handler):
    @tornado.web.asynchronous
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        data = self.get_body_argument("data")
        index = get_index(username)

        print "username:%s    password:%s    index:%d" % (username, password, index)

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return

        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return

        l = len(data)
        if l > 20 * 1024:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return

        ping(index)
        cur = db[index].cursor()
        sql = "select password, data from user where username = '%s'" % (username)
        cur.execute(sql)
        res = cur.fetchall()

        if len(res) > 1:
            # 未知问题
            print "unknow error -2"
            self.write('{"result":"-2"}')
            self.finish()
            return
        elif len(res) == 0:
            # 未注册
            print "register error -4"
            self.write('{"result":"-4"}')
            self.finish()
            return
        else:
            pw = res[0][0]
            old_data = res[0][1]
            old_gold = 0
            try:
                s = json.loads(old_data)
                for i in range(len(s)):
                    if s[i]["key"] == "m_gold":
                        old_gold = int(s[i]["Value"])
                        break
            except:
                pass
            new_gold = 0
            try:
                s = json.loads(data)
                for i in range(len(s)):
                    if s[i]["key"] == "m_gold":
                        new_gold = int(s[i]["Value"])
                        break
            except:
                pass
            if old_gold != 0 and new_gold != 0:
                if new_gold < 0 or new_gold - old_gold > 100000:
                    sql = "update user set dt = UNIX_TIMESTAMP() + 86400 * 1000 where username = %s"
                    param = (username,)
                    cur.execute(sql, param)
                    # 作弊
                    print "zuobi -5"
                    self.write('{"result":"-5"}')
                    self.finish()
                    return
                
            if pw != password:
                # 密码错误
                print "password error -1"
                self.write('{"result":"-1"}')
                self.finish()
                return
            
            sql = "update user set data = %s where username = %s"
            param = (data, username,)
            cur.execute(sql, param)
            # 成功
            print "save suc 0"
            self.write('{"result":"0"}')
            self.finish()

class code_handler(base_handler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_body_argument("username")
        index = get_index(username)

        print "username:%s    index:%d" % (username, index)

        ping(index)
        cur = db[index].cursor()
        sql = "select code from user where username = '%s'" % (username)
        cur.execute(sql)
        res = cur.fetchall()

        if len(res) > 1:
            # 未知问题
            print "unknow error -2"
            self.write('{"result":"-2"}')
            self.finish()
            return
        elif len(res) == 0:
            # 未注册
            print "register error -4"
            self.write('{"result":"-4"}')
            self.finish()
            return
        else:
            # 成功
            code = res[0][0]
            print "code suc 0"
            self.write('{"result":"0", "code":"%s"}' % code)
            self.finish()

class lock_handler(base_handler):
    @tornado.web.asynchronous
    def post(self):
        # 收到包，取出地址信息
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        index = get_index(username)

        print "username:%s    password:%s    index:%d" % (username, password, index)

        l = len(username)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
            self.write('{"result":"-3"}')
            self.finish()
            return

        l = len(password)
        if l < 5 or l > 16:
            # 长度问题
            print "len error -3"
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
            print "unknow error -2"
            self.write('{"result":"-2"}')
            self.finish()
            return
        elif len(res) == 0:
            # 未注册
            print "register error -4"
            self.write('{"result":"-4"}')
            self.finish()
            return
        else:
            pw = res[0][0]
            if pw != password:
                # 密码错误
                print "password error -1"
                self.write('{"result":"-1"}')
                self.finish()
                return
            else:
                sql = "update user set dt = UNIX_TIMESTAMP() + 86400 * 3 where username = %s"
                param = (username,)
                cur.execute(sql, param)
                # 成功
                print "lock suc 0"
                self.write('{"result":"0"}')
                self.finish()

class cd_handler(tornado.web.RequestHandler):
    def get(self):
        self.write('<?xml version="1.0"?><cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>')
        
class Application(tornado.web.Application):  
    def __init__(self):  
        handlers = [
            (r"/regsiter", regitser_handler),
            (r"/load", load_handler),
            (r"/save", save_handler),
            (r"/code", code_handler),
            (r"/lock", lock_handler),
            (r"/crossdomain.xml", cd_handler),
        ]
        tornado.web.Application.__init__(self, handlers)

def main():
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8001)
    print 'Welcome to the machine...'
    tornado.ioloop.IOLoop.instance().start()
            
if __name__ == '__main__':
    main()

