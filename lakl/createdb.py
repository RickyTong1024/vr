#!/usr/bin/env python  
#coding=utf-8

import sys
import MySQLdb

def main():
    for i in range(20):
        db = MySQLdb.connect(user='root', passwd='1qaz2wsx@39299911', db='lakluser' + str(i), host='')    
        cur = db.cursor()
        sql = "drop table user"
        cur.execute(sql)
        sql = "create table user (id int not null primary key, username text, password text, data blob, code text, dt bigint)"
        cur.execute(sql)
        db.close()
            
if __name__ == '__main__':
    main()
