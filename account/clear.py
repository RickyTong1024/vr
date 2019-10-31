#!/usr/bin/env python  
#coding=utf-8

import sys
import MySQLdb
import json
import time

#cpasswd='1qaz2wsx@39299911'
#chost='121.40.80.198'
cpasswd='root'
chost='127.0.0.1'

def main(index):
    cdb='tsvruser' + str(index)
    db = MySQLdb.connect(user='root' ,passwd=cpasswd ,db=cdb, host=chost)
    cur = db.cursor()
    flag = True
    num = 0
    tnum = 0
    while flag:
        if tnum % 1000 == 0:
            print tnum
        sql = "select username, data from user limit %s, 100"
        param = (num,)
        cur.execute(sql, param)
        params = []
        res = cur.fetchall()
        num = num + 100
        tnum = tnum + 100
        if len(res) < 100:
            flag = False
        for i in range(len(res)):
            name = res[i][0]
            s = res[i][1]
            flag1 = False
            lastTime = 9999999999999
            gold = 0
            try:
                s = json.loads(s)
                for j in range(len(s)):
                    if s[j]["key"] == "m_gold":
                        gold = int(s[j]["Value"])
                    if s[j]["key"] == "LastLoginTime_NEW":
                        tmp = int(s[j]["Value"]) - 62135596800000
                        if tmp < lastTime:
                            lastTime = tmp
                if gold >= 2000000 or gold < 0:
                    flag1 = True
                elif time.time() * 1000 - lastTime > 86400000 * 30:
                    flag1 = True
            except:
                flag1 = True
            if flag1:
                params.append((name,))
                num = num - 1
            else:
                print i, name
        sql1 = "delete from user where username = %s"
        cur.executemany(sql1, params)
        time.sleep(1)
    db.close()
            
if __name__ == '__main__':
    index = sys.argv[1]
    main(index)

