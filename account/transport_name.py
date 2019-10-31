#!/usr/bin/env python  
#coding=utf-8

import sys
import MySQLdb
import json
import time
import binascii

def get_index(s):
    return binascii.crc32(s) % 20

def main():
    names = []
    for i in range(20):
        names.append([])
    db = MySQLdb.connect(user='root' ,passwd='1qaz2wsx@39299911' ,db='tsvruser', host='121.40.80.198')
    cur = db.cursor()
    sql = "select username from user"
    cur.execute(sql)
    res = cur.fetchall()
    print "read ok"
    for i in range(len(res)):
        tusername = res[i][0]
        tindex = get_index(tusername)
        names[tindex].append((tusername, "", "", 0, 0,))
    print "seperate ok"
    for i in range(20):
        print "insert", i
        tdb = MySQLdb.connect(user='root', passwd='root', db='tsvruser' + str(i), host='127.0.0.1')
        cur1 = tdb.cursor()
        sql1 = "insert into user (username, password, data, code, dt) values (%s, %s, %s, %s, %s)"
        cur1.executemany(sql1, names[i])
        tdb.close()
    db.close()
      
            
if __name__ == '__main__':
    main()
