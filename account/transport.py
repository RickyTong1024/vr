#!/usr/bin/env python  
#coding=utf-8

import sys
import MySQLdb
import json
import time
import binascii

dbnum = 0

def get_index(s):
    return binascii.crc32(s) % 20

def main():
    db = MySQLdb.connect(user='root' ,passwd='1qaz2wsx@39299911' ,db='tsvruser', host='121.40.80.198')    
    tdb = MySQLdb.connect(user='root', passwd='root', db='tsvruser' + str(dbnum), host='127.0.0.1')
    cur = tdb.cursor()
    sql = "select username from user"
    cur.execute(sql)
    res = cur.fetchall()
    for i in range(len(res)):
        tname = res[i][0]
        cur1 = db.cursor()
        sql1 = "select password, data, code, dt from user where username = %s"
        param1 = (tname,)
        cur1.execute(sql1, param1)
        res1 = cur1.fetchall()
        sql2 = "update user set password = %s, data = %s, code = %s, dt = %s where username = %s"
        param2 = (res1[0][0], res1[0][1], res1[0][2], res1[0][3], tname,)
        cur.execute(sql2, param2)
    db.close()
    tdb.close()
            
if __name__ == '__main__':
    if len(sys.argv) == 2:
        dbnum = int(sys.argv[1])
        main()
