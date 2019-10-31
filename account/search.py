#!/usr/bin/env python  
#coding=utf-8

import sys
import MySQLdb
import binascii

def get_index(s):
    return binascii.crc32(s) % 20

def search(username):
        index = get_index(username)
        db = MySQLdb.connect(user='root', passwd='1qaz2wsx@39299911', db='tsvruser' + str(index), host='121.40.106.30')
        cur = db.cursor()
        sql = "select password from user where username = '%s'" % (username)
        cur.execute(sql)
        res = cur.fetchall()

        if len(res) > 1:
            print "unknow error"
            return
        elif len(res) == 0:
            print "can not find"
            return
        else:
            print "password:", res[0][0]
            
if __name__ == '__main__':
    if len(sys.argv) == 2:
        search(sys.argv[1])

