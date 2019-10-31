#!/usr/bin/env python  
#coding=utf-8

import sys
import MySQLdb
import json

cdb='tsvruser'
cpasswd='1qaz2wsx@39299911'
chost='121.40.80.198'
#cpasswd='root'
#chost='192.168.2.66'

def main():
    db = MySQLdb.connect(user='root' ,passwd=cpasswd ,db=cdb, host=chost)
    cur = db.cursor()
    flag = True
    num = 0
    names = []
    while flag:
        if num % 1000 == 0:
            print num
        sql = "select username, data from user limit %s, 100" % num
        param = ()
        cur.execute(sql, param)
        res = cur.fetchall()
        num = num + 100
        if len(res) < 100:
            flag = False
        for i in range(len(res)):
            name = res[i][0]
            s = res[i][1]
            try:
                s = json.loads(s)
                for i in range(len(s)):
                    if s[i]["key"] == "m_gold":
                        gold = int(s[i]["Value"])
                        if gold >= 2000000 or gold < 0:
                            names.append(name + " " + str(gold) + "\n")
                            sql1 = "delete from user where username = %s"
                            param = (name,)
                            cur.execute(sql1, param)
                        break
            except:
                pass
    
    f = open("a.txt", "w")
    f.writelines(names)
    f.close()
            
if __name__ == '__main__':
    main()

